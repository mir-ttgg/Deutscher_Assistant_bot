from datetime import datetime

from sqlalchemy import select

from .config import AsyncSessionLocal
from .models import User
from sqlalchemy.dialects.postgresql import insert


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


async def is_blocked(user_id: int) -> bool:
    """Проверить, заблокирован ли пользователь"""
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return True if user.count > 100 else False


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
