# batch_repository.py
import asyncpg
import abc
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


class AsyncpgRepository(AbstractRepository):
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def add(self, batch: batch.Batch):
        await self.connection.execute(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES ($1, $2, $3, $4)",
            batch.reference,
            batch.sku,
            batch._purchased_quantity,
            batch.eta,
        )

    async def get(self, reference) -> batch.Batch:
        result = await self.connection.fetchrow(
            "SELECT * FROM batches WHERE reference = $1", reference
        )
        if result:
            return batch.Batch(
                reference=result["reference"],
                sku=result["sku"],
                _purchased_quantity=result["_purchased_quantity"],
                eta=result["eta"],
            )
        return None

    async def list(self):
        results = await self.connection.fetch("SELECT * FROM batches")
        return [
            batch.Batch(
                reference=row["reference"],
                sku=row["sku"],
                _purchased_quantity=row["_purchased_quantity"],
                eta=row["eta"],
            )
            for row in results
        ]
