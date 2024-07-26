import pytest
from app.infrastructure import batch_repository
from app.application.order_service import OrderService, InvalidSku


class FakeRepository(batch_repository.AbstractRepository):
    def __init__(self, batches=[]):
        self._batches = set(batches)

    async def add(self, batch):
        self._batches.add(batch)

    async def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    async def list(self):
        return list(self._batches)


class FakeSession:
    def __init__(self):
        self.committed = False

    def commit(self):
        self.committed = True
        print("Committed")

@pytest.mark.asyncio
async def test_add_batch():
    repo, session = FakeRepository(), FakeSession()
    service = OrderService(repo=repo, session=session)
    await service.add_batch("b1", "SOME-PRETTY-TABLE", 100, None)
    assert await repo.get("b1") is not None
    assert session.committed

@pytest.mark.asyncio
async def test_allocate_returns_allocation():
    repo, session = FakeRepository(), FakeSession()
    service = OrderService(repo=repo, session=session)
    await service.add_batch("batch-1", "SOME-PRETTY-TABLE", 100, None)
    result = await service.allocate("order-1", "SOME-PRETTY-TABLE", 10)
    assert result == "batch-1"

@pytest.mark.asyncio
async def test_allocate_errors_invalid_sku():
    repo, session = FakeRepository(), FakeSession()
    service = OrderService(repo=repo, session=session)
    await service.add_batch("batch-1", "WHITE-MIDDLE-TABLE", 100, None)

    with pytest.raises(InvalidSku, match="Invalid sku GREY-MIDDLE-TABLE"):
        await service.allocate("order-1", "GREY-MIDDLE-TABLE", 10)

@pytest.mark.asyncio
async def test_commits():
    repo, session_1 = FakeRepository(), FakeSession()
    session_2 = FakeSession()
    print(session_1.committed, session_2.committed)
    service = OrderService(repo=repo, session=session_1)
    await service.add_batch("batch-11", "WHITE-LED-LAMP", 100, None)
    service2 = OrderService(repo=repo, session=session_2)
    await service2.allocate("order-12", "WHITE-LED-LAMP", 2)
    print(session_1.committed, session_2.committed)
    assert session_1.committed is True
    assert session_2.committed is True
