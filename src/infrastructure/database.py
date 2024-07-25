from sqlalchemy import create_engine
from src.infrastructure.orm import metadata, start_mappers
from sqlalchemy.orm import sessionmaker
from config import Settings

settings = Settings()

def get_postgres_session():
    engine = create_engine(settings.db_uri())
    metadata.create_all(engine)
    start_mappers()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()  # type: ignore

def get_in_memory_session():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    start_mappers()
    return sessionmaker(bind=engine)()  # type: ignore

def get_session():
    return get_postgres_session() if settings.testing else get_in_memory_session()

def get_repository():
    from src.infrastructure.repository import SqlAlchemyRepository
    return SqlAlchemyRepository(get_session())

SessionLocal = get_session
