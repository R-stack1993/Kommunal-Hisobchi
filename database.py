# database.py
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import BigInteger, String, Float, DateTime, Integer, ForeignKey, extract, asc, desc, delete, func, update, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, default='uz')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

class House(Base):
    __tablename__ = "houses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    house_id: Mapped[int] = mapped_column(Integer, ForeignKey("houses.id", ondelete="CASCADE"), nullable=False)
    utility_type: Mapped[str] = mapped_column(String, nullable=False)
    reading_value: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- USERS & ADMIN LOGIC ---
async def add_user(telegram_id: int, full_name: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        if not result.scalar():
            new_user = User(telegram_id=telegram_id, full_name=full_name)
            session.add(new_user)
            await session.commit()

async def get_all_users() -> list[int]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.telegram_id))
        return list(result.scalars().all())

async def count_users() -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(User.id)))
        return result.scalar()

async def get_all_users_detailed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

async def set_user_ban_status(telegram_id: int, status: bool) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(is_banned=status)
        )
        await session.commit()
        return result.rowcount > 0

async def check_if_banned(telegram_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.is_banned).where(User.telegram_id == telegram_id))
        return bool(result.scalar())

async def get_user_language(telegram_id: int) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.language).where(User.telegram_id == telegram_id))
        lang = result.scalar()
        return lang if lang else 'uz'

async def set_user_language(telegram_id: int, lang: str):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(language=lang)
        )
        await session.commit()

# --- HOUSE LOGIC ---
async def get_user_houses(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(House).where(House.telegram_id == telegram_id).order_by(House.id))
        return result.scalars().all()

async def get_house_by_id(house_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(House).where(House.id == house_id))
        return result.scalar()

async def add_house(telegram_id: int, name: str) -> bool:
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(func.count(House.id)).where(House.telegram_id == telegram_id))
        if res.scalar() >= 5:
            return False
        new_house = House(telegram_id=telegram_id, name=name)
        session.add(new_house)
        await session.commit()
        return True

async def delete_house(house_id: int, telegram_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Reading).where(Reading.house_id == house_id))
        result = await session.execute(delete(House).where(House.id == house_id, House.telegram_id == telegram_id))
        await session.commit()
        return result.rowcount > 0

# --- READINGS LOGIC ---
async def get_readings_context(telegram_id: int, house_id: int, utility_type: str):
    async with AsyncSessionLocal() as session:
        query_last = select(Reading).where(
            Reading.telegram_id == telegram_id,
            Reading.house_id == house_id,
            Reading.utility_type == utility_type
        ).order_by(desc(Reading.created_at)).limit(1)
        last_res = await session.execute(query_last)
        last_record = last_res.scalar()

        if not last_record:
            return None, None, None

        now = datetime.now()
        
        query_curr_start = select(Reading.reading_value).where(
            Reading.telegram_id == telegram_id,
            Reading.house_id == house_id,
            Reading.utility_type == utility_type,
            extract('year', Reading.created_at) == now.year,
            extract('month', Reading.created_at) == now.month
        ).order_by(asc(Reading.created_at)).limit(1)
        curr_res = await session.execute(query_curr_start)
        curr_month_start = curr_res.scalar()

        query_prev_start = select(Reading.reading_value).where(
            Reading.telegram_id == telegram_id,
            Reading.house_id == house_id,
            Reading.utility_type == utility_type,
            extract('year', Reading.created_at) == last_record.created_at.year,
            extract('month', Reading.created_at) == last_record.created_at.month
        ).order_by(asc(Reading.created_at)).limit(1)
        prev_res = await session.execute(query_prev_start)
        prev_month_start = prev_res.scalar()
        
        if prev_month_start is None:
            prev_month_start = last_record.reading_value

        return last_record, curr_month_start, prev_month_start

async def save_new_reading(telegram_id: int, house_id: int, utility_type: str, reading_value: float):
    async with AsyncSessionLocal() as session:
        new_reading = Reading(
            telegram_id=telegram_id,
            house_id=house_id,
            utility_type=utility_type,
            reading_value=reading_value
        )
        session.add(new_reading)
        await session.commit()

async def delete_last_reading(telegram_id: int, house_id: int, utility_type: str) -> bool:
    async with AsyncSessionLocal() as session:
        query = select(Reading).where(
            Reading.telegram_id == telegram_id,
            Reading.house_id == house_id,
            Reading.utility_type == utility_type
        ).order_by(desc(Reading.created_at)).limit(1)
        
        result = await session.execute(query)
        last_record = result.scalar()
        
        if last_record:
            await session.delete(last_record)
            await session.commit()
            return True
        return False

async def delete_all_readings_for_house(telegram_id: int, house_id: int, utility_type: str) -> int:
    async with AsyncSessionLocal() as session:
        query = delete(Reading).where(
            Reading.telegram_id == telegram_id,
            Reading.house_id == house_id,
            Reading.utility_type == utility_type
        )
        result = await session.execute(query)
        await session.commit()
        return result.rowcount

async def get_monthly_usage_data(telegram_id: int, house_id: int, utility_type: str):
    async with AsyncSessionLocal() as session:
        query = select(Reading).where(
            Reading.telegram_id == telegram_id,
            Reading.house_id == house_id,
            Reading.utility_type == utility_type
        ).order_by(asc(Reading.created_at))
        
        result = await session.execute(query)
        readings = result.scalars().all()
        
        monthly_max = {}
        for r in readings:
            key = f"{r.created_at.year}-{r.created_at.month:02d}"
            if key not in monthly_max or r.reading_value > monthly_max[key]:
                monthly_max[key] = r.reading_value
        
        sorted_months = sorted(monthly_max.keys())
        if len(sorted_months) < 2:
            return []
            
        UZ_MONTHS = {
            "01":"Yan", "02":"Fev", "03":"Mart", "04":"Apr", 
            "05":"May", "06":"Iyun", "07":"Iyul", "08":"Avg", 
            "09":"Sen", "10":"Okt", "11":"Noy", "12":"Dek"
        }
        
        usage_data = []
        for i in range(1, len(sorted_months)):
            prev_m = sorted_months[i-1]
            curr_m = sorted_months[i]
            usage = monthly_max[curr_m] - monthly_max[prev_m]
            year, month = curr_m.split('-')
            month_name = f"{UZ_MONTHS[month]} '{year[-2:]}"
            usage_data.append((month_name, usage))
        
        return usage_data[-6:]