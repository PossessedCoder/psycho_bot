from aiogram import Router, Dispatcher, Bot
from dotenv import load_dotenv
from os import getenv
from database.db_class import Base, engine
import asyncio
from handlers.handlers import router


async def init_models():
    async with engine.begin() as conn:
        # run_sync выполняет синхронные методы (DDL) в асинхронном драйвере
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы созданы!")


async def main():
    load_dotenv('.env')
    bot = Bot(token=getenv('TOKEN'))
    dp = Dispatcher()
    await init_models()
    dp.include_router(router=router)
    print(await bot.get_me())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

