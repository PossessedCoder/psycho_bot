from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db_class import async_session, User, Test

def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            try:
                # Явно не открываем транзакции, так как они уже есть в контексте
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию

    return wrapper

@connection
async def get_tests(session: AsyncSession):
    req = select(Test)
    return (await session.scalars(req)).fetchall()

@connection
async def get_users(session: AsyncSession):
    req = select(User)
    return (await session.scalars(req)).fetchall()

@connection
async def add_user(session: AsyncSession, tg_id, username, first_name):
    session.add(User(telegram_id=tg_id, username=username, first_name=first_name))
    await session.commit()

@connection
async def add_test_to_database(session: AsyncSession, test_name, filename):
    session.add(Test(name=test_name, file_name=filename))

async def get_test_filename_by_name(session: AsyncSession, name):
    req = select(Test).where(Test.name == name)
    return (await session.scalars(req)).one().file_name