# drop_tables.py
import asyncio
from database import engine, Base

async def drop_all():
    print("Jadvallar o'chirilmoqda...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Barcha jadvallar muvaffaqiyatli o'chirildi! Endi main.py ni ishga tushiring.")

if __name__ == "__main__":
    asyncio.run(drop_all())