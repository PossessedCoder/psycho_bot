from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram import F, Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.testing.suite.test_reflection import users

from utils.json_utils import get_data
from aiogram import types
from utils.utils import simple_inline, show_main_menu, delete_message_safe, get_main_keyboard
import logging
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup
from math import ceil
CHANNEL_USERNAME = "@dariainpsycho"
CHANNEL_LINK = "https://t.me/dariainpsycho"
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
        if isinstance(message, types.Message):
            await message.answer('главное сообщение', reply_markup=await get_main_keyboard())
            await message.answer('Главное сообщение 2', reply_markup=await simple_inline([[['Тесты', 'main_test']], [['Путеводитель по каналу', 'channel_guide'], ['Запись на консультацию', 'https://t.me/dariainpsycho/15|url']]]))
        else:
            await message.message.answer('главное сообщение', reply_markup=await get_main_keyboard())
            await message.message.answer('Главное сообщение 2', reply_markup=await simple_inline([[['Тесты', 'main_test']],
                                                                                          [['Путеводитель по каналу',
                                                                                            'channel_guide'],
                                                                                           ['Запись на консультацию',
                                                                                            'https://t.me/dariainpsycho/15|url']]]))
    else:
        print(2)
        if isinstance(message, types.Message):

            await show_subscription_request(message)
        else:
            await show_subscription_request(message.message)


@router.callback_query(F.data == 'to_start')
@router.message(F.text == 'Главная страница')
async def main_message(message: CallbackQuery | Message, bot):
    user_id = message.from_user.id
    if await check_subscription(user_id, bot):
        print(1)
        if isinstance(message, types.Message):
            await message.answer('Главное сообщение 2', reply_markup=await simple_inline([[['Тесты', 'main_test']],
                                                                                          [['Путеводитель по каналу',
                                                                                            'channel_guide'],
                                                                                           ['Запись на консультацию',
                                                                                            'https://t.me/dariainpsycho/15|url']]]))
        else:
            await message.message.answer('Главное сообщение 2', reply_markup=await simple_inline([[['Тесты', 'main_test']],
                                                                                          [['Путеводитель по каналу',
                                                                                            'channel_guide'],
                                                                                           ['Запись на консультацию',
                                                                                            'https://t.me/dariainpsycho/15|url']]]))
    else:
        print(2)
        if isinstance(message, types.Message):
            await message.answer('главное сообщение', reply_markup=await get_main_keyboard())
            await show_subscription_request(message)
        else:
            await show_subscription_request(message.message)

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

@router.callback_query(F.data == 'main_test')
@router.message('Тесты')
async def tests(message: CallbackQuery | Message):
    if isinstance(message, CallbackQuery):
        a = await show_main_menu(message.message)
        await message.message.answer(a[0], reply_markup=a[1])
        await delete_message_safe(message.message)
    else:
        a = await show_main_menu(message)
        await message.answer(a[0], reply_markup=a[1])
        await delete_message_safe(message)

@router.callback_query(F.data == 'channel_guide')
async def channel_guide(message: CallbackQuery):
    await message.message.answer('🛠 Функция в разработке')


@router.message(F.text == 'Вопрос дня')
async def channel_guide(message: CallbackQuery):
    await message.message.answer('🛠 Функция в разработке')

@router.message(F.text == 'Профиль')
async def channel_guide(message: CallbackQuery):
    await message.message.answer('🛠 Функция в разработке')


@router.callback_query(F.data.startswith("teststart"))
async def test_start(callback: CallbackQuery, bot: Bot):
    await delete_message_safe(callback.message)
    test = callback.data.split('_')[1]
    test_data = get_data(f'config/{test}.json')
    await bot.send_message(chat_id=callback.from_user.id, text=test_data['test']['start_message'], reply_markup=await simple_inline([[['НАЧАТЬ ТЕСТ', f'{test}_question_0_0']]]))

@router.callback_query(F.data.contains('question'))
async def question_test(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await delete_message_safe(callback.message)
    test = callback.data.split('_')[0]
    question_number = int(callback.data.split('_')[2])
    test_data = get_data(f'config/{test}.json')
    answer_count = int(test_data['test']['key']['answers_count'])
    if 'back' in callback.data:
        if question_number != -1:
            data = await state.get_data()
            items = data.get('answers', [])
            items.pop(-1)
            # 3. Обновляем состояние
            await state.update_data(answers=items)
        else:
            return await cmd_start(message=callback.message, bot=bot)
    if question_number == 0:
        await state.set_state(Test.waiting_for_answer)
        await state.update_data(answers=[])
        if answer_count == 2:
            await callback.message.answer(test_data['test']['questions'][question_number], reply_markup=await simple_inline([[['ДА', f'{test}_question_{question_number + 1}_{2}'], ['НЕТ', f'{test}_question_{question_number + 1}_{1}']], [['НАЗАД', f'{test}_question_{question_number - 1}_back_-1']]]))
        else:
            lst = [[]]
            for i in range(answer_count):
                lst[0].append([str(i + 1), f'{test}_question_{question_number + 1}_{i + 1}'])
            print(lst)
            lst.append([['НАЗАД', f'{test}_question_{question_number - 1}_back_-1']])
            await callback.message.answer(test_data['test']['questions'][question_number], reply_markup=await simple_inline(lst))
    elif question_number == len(test_data['test']['questions']):
        await callback.message.answer(text='УЗНАТЬ РЕЗУЛЬТАТЫ?', reply_markup=await simple_inline([[['РЕЗУЛЬТАТЫ', f'{test}_results_{callback.data.split('_')[-1]}']]]))
    else:
        data = await state.get_data()
        items = data.get('answers', [])
        if callback.data.split('_')[-1] != '-1':
        # 2. Добавляем
            items.append(callback.data.split('_')[-1])

            # 3. Обновляем состояние
            await state.update_data(answers=items)
        if answer_count == 2:
            await callback.message.answer(test_data['test']['questions'][question_number], reply_markup=await simple_inline([[['ДА', f'{test}_question_{question_number + 1}_{2}'], ['НЕТ', f'{test}_question_{question_number + 1}_{1}']], [['НАЗАД', f'{test}_question_{question_number - 1}_back_-1']]]))
        else:
            lst = [[]]
            for i in range(answer_count):
                lst[0].append([str(i + 1), f'{test}_question_{question_number + 1}_{i + 1}'])
            lst.append([['НАЗАД', f'{test}_question_{question_number - 1}_back_-1']])
            print(lst)
            await callback.message.answer(test_data['test']['questions'][question_number], reply_markup=await simple_inline(lst))

@router.callback_query(F.data.contains('results'))
async def results(callback: CallbackQuery, state: FSMContext):
    await delete_message_safe(callback.message)
    test = callback.data.split('_')[0]
    test_data = get_data(f'config/{test}.json')
    keys: dict = test_data['test']['key']
    answers = (await state.get_data())['answers']
    answers.append(callback.data.split('_')[-1])
    answers = list(map(int, answers))
    types = test_data['test']['types']
    answer_count = int(test_data['test']['key']['answers_count'])
    print(keys)
    if answer_count == 2:
        lst = [0] * len(list(keys.keys())[1::])
        for i in list(keys.keys())[1::]:
            print(i)
            c = 0
            d = 0
            for j in keys[i]['yes'].keys():
                print(answers[int(j) - 1], keys[i]['yes'][j])
                if answers[int(j) - 1] in keys[i]['yes'][j]:
                    c += 1
            for j in keys[i]['no'].keys():
                if answers[int(j) - 1] not in keys[i]['no'][j]:
                    d += 1
            print(c, d)
            lst[list(keys.keys())[1::].index(i)] += c + d
        if lst.count(max(lst)) > 1:
            await callback.message.answer(
                text='Вы невнимательно проходили тест, результаты получить не удалось. Пройти ещё раз?',
                reply_markup=await simple_inline([[['ДА', f'teststart_{test}'], ['НЕТ', 'to_start']]]))
        else:
            ty = types[list(keys.keys())[1::][lst.index(max(lst))]]
            name = ty['name']
            desc = ty['description']
            char = ty['characteristics']
            await callback.message.answer(
                text=f'{name}\n\n{desc}\n\n', reply_markup=await simple_inline([[['Читать', f'{CHANNEL_LINK}|url']], [['ВЕРНУТЬСЯ К ТЕСТАМ', 'to_start']]]))
        print(lst)
    else:
        a = ceil(answer_count / 2)
        print(a)
        lst = [0] * len(list(keys.keys())[1::])
        for i in list(keys.keys())[1::]:
            print(i)
            c = 0
            d = 0
            for j in keys[i]['yes'].keys():
                print(answers[int(j) - 1], keys[i]['yes'][j])
                if answers[int(j) - 1] in keys[i]['yes'][j]:
                    c += abs(a - answers[int(j) - 1])
            for j in keys[i]['no'].keys():
                if answers[int(j) - 1] in keys[i]['no'][j]:
                    d += abs(a - answers[int(j) - 1])
            print(c, d)
            lst[list(keys.keys())[1::].index(i)] += c - d
        if lst.count(max(lst)) > 1:
            await callback.message.answer(text='Вы невнимательно проходили тест, результаты получить не удалось. Пройти ещё раз?', reply_markup=await simple_inline([[['ДА', f'teststart_{test}'], ['НЕТ', 'to_start']]]))
        else:
            ty = types[list(keys.keys())[1::][lst.index(max(lst))]]
            name = ty['name']
            desc = ty['description']
            char = ty['characteristics']
            await callback.message.answer(text=f'{name}\n\n{desc}\n\n', reply_markup=await simple_inline([[['Читать', f'{CHANNEL_LINK}|url']], [['ВЕРНУТЬСЯ К ТЕСТАМ', 'to_start']]]))
        print(lst)
    await state.clear()
    print(answers)



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