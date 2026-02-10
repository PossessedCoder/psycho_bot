from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from database.db_utils import get_tests
async def delete_message_safe(message: types.Message):
    """Безопасное удаление сообщения с обработкой ошибок"""
    try:
        await message.delete()
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")
        pass

async def simple_inline(lst):
    b = InlineKeyboardBuilder()
    a = []
    for i in lst:
        a = []
        for el in i:
            if el[1].split('|')[-1] != 'url':
                a.append(InlineKeyboardButton(text=el[0], callback_data=el[1]))
            else:
                a.append(InlineKeyboardButton(text=el[0], url=el[1].split('|')[0]))

        b.row(*a)
    return b.as_markup()

# Главное меню
async def show_main_menu(message: types.Message):
    lst = [[[el.name, f'teststart_{el.file_name}']] for el in await get_tests()]
    keyboard = await simple_inline(lst)

    return ("🎯 ВЫБЕРИТЕ ТЕСТ:\n\n1. Тип привязанности - узнайте ваш стиль отношений\n2. Причина прокрастинации - поймите, что мешает действовать\n3. Акцентуация характера - определите ведущие черты личности\n\n👉 Нажмите на кнопку ниже:", keyboard)
