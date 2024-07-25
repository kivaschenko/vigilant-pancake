from typing import Optional
from datetime import date

from src.domain.entities import model
from src.adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], repo: AbstractRepository, session,) -> None:
    # TODO: Add logger here
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()


def allocate(order_id: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
    # TODO: Add logger here
    line = model.OrderLine(orderid=order_id, sku=sku, qty=qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batch_ref = model.allocate(line, batches)
    session.commit()
    return batch_ref
