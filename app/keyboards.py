from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)


def get_start_admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(
            text='Управление пользователями')],
        [KeyboardButton(
            text='Выгрузка отчёта')],
        [KeyboardButton(
            text='База знаний')]

    ], resize_keyboard=True)


def get_user_management_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить пользователя',
                              callback_data='add_user')],
        [InlineKeyboardButton(text='Список пользователей',
                              callback_data='list_users')],
        [InlineKeyboardButton(text='Удалить пользователя',
                              callback_data='delete_user')],
        [InlineKeyboardButton(text='Назад', callback_data='back_admin')]
    ])


def get_article_keyboards() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить',
                              callback_data='edit_article')],
        [InlineKeyboardButton(text='Назад', callback_data='back_admin')]
    ])


def get_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_admin')]
    ])
