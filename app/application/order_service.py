from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import model
from app.infrastructure.batch_repository import AbstractRepository


class InvalidSku(Exception):
    pass


class OrderService:
    def __init__(self, repo: AbstractRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def add_batch(self, ref: str, sku: str, qty: int, eta: Optional[date]) -> None:
        await self.repo.add(model.Batch(ref, sku, qty, eta))
        self.session.commit()

    async def allocate(self, order_id: str, sku: str, qty: int) -> str:
        line = model.OrderLine(orderid=order_id, sku=sku, qty=qty)
        batches = await self.repo.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch_ref = model.allocate(line, batches)
        self.session.commit()
        return batch_ref


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}
