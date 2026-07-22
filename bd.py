from sqlalchemy import create_engine, Column, String, Integer, text, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DB_URL = "sqlite+aiosqlite:///user.db"



engine = create_async_engine (
    DB_URL
)

new_session = async_sessionmaker(engine, expire_on_commit=False)



class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,  unique=True)
    password = Column(String)
    
async def create_tables():
    async with engine.begin() as conn: 
       await conn.run_sync(User.metadata.create_all)

async def insert_user_data():
    async with new_session() as session:
        result = await session.execute(select(User))
        if result.first() is None:  
            session.add_all([
                User(id=1, name='ivan', password='ivan556Pass'),
                User(id=2, name='denchik', password='denchik888krut'),
            ])
            await session.commit()
            return {'ok':True}

async def delete_tables():
   async with engine.begin() as conn:
       await conn.run_sync(User.metadata.drop_all)
