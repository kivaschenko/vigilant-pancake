import pytest
from src.application.order_service import OrderService, InvalidSku
from src.domain.model import Batch, OrderLine
from src.infrastructure.repository import AbstractRepository

class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def list(self):
        return list(self._batches)

class FakeSession:
    def commit(self):
        pass

def test_add_batch():
    repo = FakeRepository([])
    session = FakeSession()
    service = OrderService(repo, session)
    service.add_batch("batch1", "sku1", 100, None)
    assert repo.list() == [Batch("batch1", "sku1", 100, None)]

def test_allocate():
    repo = FakeRepository([Batch("batch1", "sku1", 100, None)])
    session = FakeSession()
    service = OrderService(repo, session)
    result = service.allocate("order1", "sku1", 10)
    assert result == "batch1"

def test_allocate_invalid_sku():
    repo = FakeRepository([Batch("batch1", "sku1", 100, None)])
    session = FakeSession()
    service = OrderService(repo, session)
    with pytest.raises(InvalidSku):
        service.allocate("order1", "sku2", 10)