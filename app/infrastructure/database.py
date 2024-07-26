# from sqlalchemy import create_engine
# from app.infrastructure.orm import metadata, start_mappers
# from sqlalchemy.orm import sessionmaker
# from config import Settings

# settings = Settings()


# def get_session():
#     engine = create_engine(settings.db_uri)
#     metadata.create_all(engine)
#     start_mappers()
#     return sessionmaker(autocommit=False, autoflush=False, bind=engine)()  # type: ignore


# def get_repository():
#     from app.infrastructure.batch_repository import SQLAlchemyRepository

#     return SQLAlchemyRepository(get_session())


# SessionLocal = get_session

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
