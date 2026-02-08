from aiogram.fsm.state import StatesGroup, State

from aiogram import F, Bot, Router
from aiogram.filters import Command, CommandStart
from utils.json_utils import get_data
from aiogram import types
from utils.utils import simple_inline, show_main_menu, delete_message_safe
import logging
from aiogram.types import CallbackQuery, Message

CHANNEL_USERNAME = "@The_Logic_of_Emotions"
CHANNEL_LINK = "https://t.me/The_Logic_of_Emotions"
router = Router()
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Test(StatesGroup):
    waiting_for_answer = State()

# Функция проверки подписки
async def check_subscription(user_id: int, bot: Bot) -> bool:
    try:
        chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    if await check_subscription(user_id, bot):
        print(1)
        a = await show_main_menu(message)
        await message.answer(a[0], reply_markup= a[1])
    else:
        print(2)
        await show_subscription_request(message)


# Показать меню подписки
async def show_subscription_request(message: types.Message):
    keyboard = await simple_inline([
        [["📢 Подписаться на канал", f'{CHANNEL_LINK}|url']],
        [["✅ Я подписался, проверить", "check_subscription"]]
    ])

    await message.answer(
        "🔒 Доступ к тестам закрыт\n\n"
        "Чтобы открыть функции бота, необходимо подписаться на наш канал:\n"
        f"{CHANNEL_LINK}\n\n"
        "После подписки нажмите кнопку 'Я подписался, проверить'",
        reply_markup=keyboard
    )




@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, bot: Bot):
    if await check_subscription(callback.from_user.id, bot):
        await callback.answer("✅ Подписка оформлена! Функции доступны", show_alert=False)
        await show_main_menu(callback.message)
    else:
        await callback.answer("❌ Вы ещё не подписались на канал", show_alert=True)

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    await show_main_menu(callback.message)
    await callback.answer()