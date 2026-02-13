from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram import Router, F
import logging
from os import getenv
from aiogram.filters import CommandStart
from datebase.crud import add_user, get_user_by_id, is_blocked, delete_user
from app.keyboards import get_start_admin_keyboard, get_user_management_keyboard, get_article_keyboards
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datebase.config import generate_users_report
import io
from datebase.config import AsyncSessionLocal
from ai import ASSISTANT_ID, client


class AddUser(StatesGroup):
    waiting_for_user_id = State()


class DeleteUser(StatesGroup):
    waiting_for_user_id = State()


router = Router()
MANAGER_ID = [int(x) for x in getenv('MANAGER_ID', '').split(',') if x]


@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id in MANAGER_ID:
        await message.answer('Выберите действие', reply_markup=get_start_admin_keyboard())

    else:
        try:
            user = await get_user_by_id(message.from_user.id)
            if user is None:
                await message.answer('❌ У вас нет доступа. Пожалуйста, обратитесь к своему куратору для получения доступа к сервису.')
                return
            else:
                if await is_blocked(message.from_user.id):
                    await message.answer('К сожалению, вы исчерпали лимит вопросов на эту неделю. Счетчик обновляется по понедельникам.')
                    return
                else:
                    await message.answer('✅ Добро пожаловать! Вы успешно авторизовались.')
        except Exception as e:
            logging.info(f'Ошибка получения пользователя: {e}')


@router.message(F.from_user.id.in_(MANAGER_ID), F.text == 'Управление пользователями')
async def manage_users(message: Message):
    await message.answer('Выберите действие:', reply_markup=get_user_management_keyboard())


def is_valid_user_id_format(value: str) -> bool:
    '''
    Проверяет, что строка является целым положительным числом.
    '''
    try:
        user_id = int(value)
        return user_id > 0
    except (ValueError, TypeError):
        return False


@router.callback_query(F.data == 'back_admin')
async def back_to_admin(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer(
        'Вы в главном меню:',
        reply_markup=get_start_admin_keyboard()
    )
    await callback_query.answer()


async def back_to_admin_msg(message):
    await message.answer(
        'Вы в главном меню:',
        reply_markup=get_start_admin_keyboard()
    )


@router.callback_query(F.data == 'add_user')
async def add_user_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        text='Введите Telegram ID пользователя',
        reply_markup=None
    )
    # await callback_query.message.answer('Введите Telegram ID пользователя')
    await state.set_state(AddUser.waiting_for_user_id)


@router.message(AddUser.waiting_for_user_id)
async def add_user_receive(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        if not is_valid_user_id_format(str(user_id)):
            await message.answer('Неверный формат Telegram ID. Пожалуйста, введите положительное целое число.')
            await back_to_admin_msg(message)
            await state.clear()
            return
        await add_user(user_id, 'unknown')
        logging.info(
            f'Пользователь {user_id} добавлен менеджером {message.from_user.id}')
        await message.answer('Пользователь добавлен')
        await back_to_admin_msg(message)
        await state.clear()
        return
    except Exception as e:
        logging.info(f'Ошибка добавления пользователя: {e}')
        await message.answer('Неверный формат Telegram ID. Пожалуйста, введите положительное целое число.')
        await back_to_admin_msg(message)
        await state.clear()
        return


@router.callback_query(F.data == 'list_users')
async def list_users_callback(callback_query: CallbackQuery, session: AsyncSessionLocal):
    try:
        file_stream = await generate_users_report(session)

        # Формируем имя файла с датой
        filename = 'users_list.xlsx'
        await callback_query.message.edit_text(
            text='Формирую отчёт, пожалуйста, подождите...',
            reply_markup=None
        )
        # Создаем объект файла для отправки
        document = BufferedInputFile(
            file=file_stream.read(),
            filename=filename
        )

        # Отправляем файл
        await callback_query.message.answer_document(
            document=document,
            caption="📋 Список пользователей"
        )

        await callback_query.answer('Отчёт сформирован')
    except Exception as e:
        logging.error(f'Ошибка при генерации отчёта: {e}')
        await callback_query.message.answer('Не удалось сформировать отчёт')
        await callback_query.answer()


@router.callback_query(F.data == 'delete_user')
async def delete_user_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        text='Введите Telegram ID пользователя для удаления',
        reply_markup=None
    )
    await state.set_state(DeleteUser.waiting_for_user_id)


@router.message(DeleteUser.waiting_for_user_id)
async def delete_user_receive(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        if not is_valid_user_id_format(str(user_id)):
            await message.answer('Неверный формат Telegram ID. Пожалуйста, введите положительное целое число.')
            await back_to_admin_msg(message)
            await state.clear()
            return
        if await delete_user(user_id):
            logging.info(
                f'Пользователь {user_id} удален менеджером {message.from_user.id}')
            await message.answer('Пользователь удален')
            await back_to_admin_msg(message)
            await state.clear()
            return
        else:
            await message.answer('Пользователь не найден')
            await back_to_admin_msg(message)
            await state.clear()
            return
    except Exception as e:
        logging.info(f'Ошибка удаления пользователя: {e}')
        await message.answer('Неверный формат Telegram ID. Пожалуйста, введите положительное целое число.')
        await back_to_admin_msg(message)
        await state.clear()
        return


@router.message(F.from_user.id.in_(MANAGER_ID), F.text == 'Выгрузка отчёта')
async def export_report_callback(message: Message):
    await message.answer('Функция пока не реализована.')


@router.message(F.from_user.id.in_(MANAGER_ID), F.text == 'База знаний')
async def knowledge_base_callback(message: Message):
    await message.answer('Выберите действие:', reply_markup=get_article_keyboards())
