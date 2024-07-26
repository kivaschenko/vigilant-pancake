import uuid
import httpx
from config import settings


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


async def post_to_add_batch(ref, sku, qty, eta):
    url = settings.api_url
    print(url, "<- url")
    data = {"ref": ref, "sku": sku, "qty": qty, "eta": eta}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost:8000") as client:
        r = await client.post("/batches", json=data)
        print(r.json(), r.status_code, r.text)
        assert r.status_code == 201
