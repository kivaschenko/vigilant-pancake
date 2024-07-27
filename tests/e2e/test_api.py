from httpx import AsyncClient, ASGITransport
import pytest
import uuid

from app.main import (
    app as current_app,
)  # noqa Ensure you imported your FastAPI app instance


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


async def post_to_add_batch(ref, sku, qty, eta):
    data = {"ref": ref, "sku": sku, "qty": qty, "eta": eta}
    transport = ASGITransport(app=current_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/batches", json=data)
        print(r.json(), r.status_code, r.text)
        assert r.status_code == 201


@pytest.mark.asyncio
async def test_root(postgres_db):
    transport = ASGITransport(app=current_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World", "result": 1}


@pytest.mark.asyncio
async def test_happy_path_returns_201_and_allocated_batch(postgres_db):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)

    await post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    await post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    await post_to_add_batch(otherbatch, othersku, 100, None)

    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}

    transport = ASGITransport(app=current_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


@pytest.mark.asyncio
async def test_unhappy_path_returns_400_and_error_message(postgres_db):
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}

    transport = ASGITransport(app=current_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/allocate", json=data)

    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
