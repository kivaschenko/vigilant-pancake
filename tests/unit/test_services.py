import pytest
from app.infrastructure import batch_repository
from app.application.order_service import OrderService, InvalidSku


class FakeRepository(batch_repository.AbstractRepository):
    def __init__(self, batches=[]):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = FakeRepository(), FakeSession()
    service = OrderService(repo=repo, session=session)
    service.add_batch("b1", "SOME-PRETTY-TABLE", 100, None)
    assert repo.get("b1") is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository(), FakeSession()
    service = OrderService(repo=repo, session=session)
    service.add_batch("batch-1", "SOME-PRETTY-TABLE", 100, None)
    result = service.allocate("order-1", "SOME-PRETTY-TABLE", 10)
    assert result == "batch-1"


def test_allocate_errors_invalid_sku():
    repo, session = FakeRepository(), FakeSession()
    service = OrderService(repo=repo, session=session)
    service.add_batch("batch-1", "WHITE-MIDDLE-TABLE", 100, None)

    with pytest.raises(InvalidSku, match="Invalid sku GREY-MIDDLE-TABLE"):
        service.allocate("order-1", "GREY-MIDDLE-TABLE", 10)


def test_commits():
    repo, session_1 = FakeRepository(), FakeSession()
    session_2 = FakeSession()
    service = OrderService(repo=repo, session=session_1)
    service.add_batch("batch-11", "WHITE-LED-LAMP", 100, None)
    service2 = OrderService(repo=repo, session=session_2)
    service2.allocate("order-12", "WHITE-LED-LAMP", 2)
    assert session_1.committed is True
    assert session_2.committed is True
