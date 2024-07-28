import pytest
from datetime import date
from app.infrastructure.database import Database


@pytest.fixture(scope="module")
async def setup_database():
    await Database.init()
    yield
    await Database._pool.close()


@pytest.fixture
async def postgres_session(setup_database):
    async with Database.get_connection() as connection:
        yield connection


@pytest.mark.asyncio
async def test_orderline_mapper_can_load_lines(postgres_session):
    await postgres_session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES ($1, $2, $3), ($4, $5, $6), ($7, $8, $9)",
        "order1",
        "RED-CHAIR",
        12,
        "order1",
        "RED-TABLE",
        13,
        "order2",
        "BLUE-LIPSTICK",
        14,
    )
    rows = await postgres_session.fetch("SELECT orderid, sku, qty FROM order_lines")
    expected = [
        ("order1", "RED-CHAIR", 12),
        ("order1", "RED-TABLE", 13),
        ("order2", "BLUE-LIPSTICK", 14),
    ]
    assert rows == expected


@pytest.mark.asyncio
async def test_orderline_mapper_can_save_lines(postgres_session):
    await postgres_session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES ($1, $2, $3)",
        "order1",
        "DECORATIVE-WIDGET",
        12,
    )
    rows = await postgres_session.fetch("SELECT orderid, sku, qty FROM order_lines")
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


@pytest.mark.asyncio
async def test_retrieving_batches(postgres_session):
    await postgres_session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES ($1, $2, $3, $4)",
        "batch1",
        "sku1",
        100,
        None,
    )
    await postgres_session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES ($1, $2, $3, $4)",
        "batch2",
        "sku2",
        200,
        date(2011, 4, 11),
    )
    rows = await postgres_session.fetch(
        "SELECT reference, sku, _purchased_quantity, eta FROM batches"
    )
    expected = [
        ("batch1", "sku1", 100, None),
        ("batch2", "sku2", 200, date(2011, 4, 11)),
    ]
    assert rows == expected


@pytest.mark.asyncio
async def test_saving_batches(postgres_session):
    await postgres_session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES ($1, $2, $3, $4)",
        "batch1",
        "sku1",
        100,
        None,
    )
    rows = await postgres_session.fetch(
        "SELECT reference, sku, _purchased_quantity, eta FROM batches"
    )
    assert rows == [("batch1", "sku1", 100, None)]


@pytest.mark.asyncio
async def test_saving_allocations(postgres_session):
    await postgres_session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES ($1, $2, $3)",
        "order1",
        "sku1",
        10,
    )
    await postgres_session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES ($1, $2, $3, $4)",
        "batch1",
        "sku1",
        100,
        None,
    )
    orderline_id = await postgres_session.fetchval(
        "SELECT id FROM order_lines WHERE orderid=$1 AND sku=$2", "order1", "sku1"
    )
    batch_id = await postgres_session.fetchval(
        "SELECT id FROM batches WHERE reference=$1 AND sku=$2", "batch1", "sku1"
    )
    await postgres_session.execute(
        "INSERT INTO allocations (orderline_id, batch_id) VALUES ($1, $2)",
        orderline_id,
        batch_id,
    )
    rows = await postgres_session.fetch(
        "SELECT orderline_id, batch_id FROM allocations"
    )
    assert rows == [(orderline_id, batch_id)]


@pytest.mark.asyncio
async def test_retrieving_allocations(postgres_session):
    await postgres_session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES ($1, $2, $3)",
        "order1",
        "sku1",
        12,
    )
    orderline_id = await postgres_session.fetchval(
        "SELECT id FROM order_lines WHERE orderid=$1 AND sku=$2", "order1", "sku1"
    )
    await postgres_session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES ($1, $2, $3, $4)",
        "batch1",
        "sku1",
        100,
        None,
    )
    batch_id = await postgres_session.fetchval(
        "SELECT id FROM batches WHERE reference=$1 AND sku=$2", "batch1", "sku1"
    )
    await postgres_session.execute(
        "INSERT INTO allocations (orderline_id, batch_id) VALUES ($1, $2)",
        orderline_id,
        batch_id,
    )
    rows = await postgres_session.fetch(
        "SELECT orderline_id, batch_id FROM allocations"
    )
    assert rows == [(orderline_id, batch_id)]
