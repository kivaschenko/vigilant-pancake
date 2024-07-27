# batch_repository.py
import abc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain import batch


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, batch: batch.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, reference) -> batch.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    async def list(self):
        raise NotImplementedError



class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, batch):
        await self.session.add(batch)
        await self.session.commit()

    async def get(self, reference) -> batch.Batch:
        result = await self.session.execute(select(batch.Batch).filter_by(reference=reference))
        return result.scalar_one()

    async def list(self):
        result = await self.session.execute(select(batch.Batch))
        return result.scalars().all()
