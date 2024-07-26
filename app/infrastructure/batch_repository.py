import abc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, reference) -> model.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    async def list(self):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, batch):
        await self.session.add(batch)

    async def get(self, reference) -> model.Batch:
        result = await self.session.query(model.Batch).filter_by(reference=reference)
        return result.scalar_one()

    async def list(self):
        result = await self.session.execute(select(model.Batch))
        return result.scalars().all()