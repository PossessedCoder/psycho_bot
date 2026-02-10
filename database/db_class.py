from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapper, Mapped, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://postgres:apple_orange_pineapple_bot_penis_ograsm@localhost:5432/psycho_bot")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(50))
    username = mapped_column(String(100))
    first_name = mapped_column(String(100))

class Test(Base):
    __tablename__ = "tests"
    id: Mapped[int] = mapped_column(primary_key=True)
    name = mapped_column(String(100))
    file_name = mapped_column(String(100))