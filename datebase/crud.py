import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from .config import AsyncSessionLocal
from .models import Query, User


async def add_user(user_id: int, username: str):
    """
    Добавляет нового пользователя или обновляет username существующего.
    """
    async with AsyncSessionLocal() as session:
        stmt = insert(User).values(
            user_id=user_id,
            username=username,
            registered_at=datetime.now()
        )
        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=['user_id'],
            set_=dict(username=username)
        )
        await session.execute(do_update_stmt)
        await session.commit()


async def get_user_by_id(user_id: int):
    """Получить пользователя по ID"""
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def reset_user_count_if_needed(user_id: int):
    """Сбрасывает счетчик, если прошла неделя"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            return

        last_monday = get_last_monday()
        if user.last_reset < last_monday:
            user.count = 0
            user.last_reset = last_monday
            await session.commit()
            logging.info(f'Счетчик сброшен для пользователя {user_id}')


async def delete_user(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True


def get_last_monday() -> datetime:
    """Получить последний понедельник 00:00 МСК"""
    now = datetime.now(tz=ZoneInfo("Europe/Moscow"))
    days_since_monday = now.weekday()  # 0 = понедельник
    last_monday = now - timedelta(days=days_since_monday)
    return last_monday.replace(hour=0, minute=0, second=0, microsecond=0)


async def reset_user_count_if_needed(user_id: int):
    """Сбрасывает счетчик, если прошла неделя"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            return

        last_monday = get_last_monday()

        if user.last_reset < last_monday:
            user.count = 0
            user.last_reset = last_monday
            await session.commit()


async def increment_user_count(user_id: int):
    """Увеличить счетчик запросов пользователя"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if user:
            user.count += 1
            await session.commit()


async def save_query(user_id: int, question: str, answer: str):
    """Сохранить вопрос-ответ в базу"""
    async with AsyncSessionLocal() as session:
        query = Query(
            user_id=user_id,
            question=question,
            answer=answer
        )
        session.add(query)
        await session.commit()


async def get_all_queries():
    """Получить все запросы для отчета"""
    async with AsyncSessionLocal() as session:
        stmt = select(Query).order_by(Query.created_at.desc())
        result = await session.execute(stmt)
        return result.scalars().all()


async def is_blocked(user_id: int) -> bool:
    """Проверить, заблокирован ли пользователь (исчерпан лимит)"""
    await reset_user_count_if_needed(user_id)

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return True
        return user.count >= 100
