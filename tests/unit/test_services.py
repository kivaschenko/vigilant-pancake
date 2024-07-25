import pytest
from src.infrastructure import repository
from src.application import order_service as services


class FakeRepository(repository.AbstractRepository):
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
    services.add_batch("b1", "SOME-PRETTY-TABLE", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository(), FakeSession()
    services.add_batch("batch-1", "SOME-PRETTY-TABLE", 100, None, repo, session)
    result = services.allocate("order-1", "SOME-PRETTY-TABLE", 10, repo, session)
    assert result == "batch-1"


def test_allocate_errors_invalid_sku():
    repo, session = FakeRepository(), FakeSession()
    services.add_batch("batch-1", "WHITE-MIDDLE-TABLE", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match='Invalid sku GREY-MIDDLE-TABLE'):
        services.allocate("order-1", "GREY-MIDDLE-TABLE", 10, repo, FakeSession())


def test_commits():
    repo, session_1 = FakeRepository(), FakeSession()
    session_2 = FakeSession()
    services.add_batch("batch-11", "WHITE-LED-LAMP", 100, None, repo, session_1)
    services.allocate("order-12", "WHITE-LED-LAMP", 2, repo, session_2)
    assert session_1.committed is True
    assert session_2.committed is True
