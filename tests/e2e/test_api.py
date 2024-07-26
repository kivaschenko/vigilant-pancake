import httpx
import pytest

from app.main import app  # noqa Ensure you imported your FastAPI app instance
from tests.utils import random_batchref, random_orderid, random_sku, post_to_add_batch


@pytest.mark.asyncio
async def test_happy_path_returns_201_and_allocated_batch():
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)

    await post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    await post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    await post_to_add_batch(otherbatch, othersku, 100, None)

    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost:8000") as client:
        r = await client.post("/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


@pytest.mark.asyncio
async def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}

    async with httpx.AsyncClient(transport=httpx.ASCITransport(app=app), base_url="http://localhost:8000") as client:
        r = await client.post("/allocate", json=data)

    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
