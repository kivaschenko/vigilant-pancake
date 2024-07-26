import pytest
from datetime import date, timedelta
from app.domain.model import Batch, OrderLine, allocate, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine("order-123", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earlist = Batch("earler-001", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("medium-001", "MINIMALIST-SPOON", 50, eta=tomorrow)
    latest = Batch("later-111", "MINIMALIST-SPOON", 80, eta=later)
    line = OrderLine("order-1123", "MINIMALIST-SPOON", 20)

    allocate(line, [earlist, medium, latest])

    assert earlist.available_quantity == 80
    assert medium.available_quantity == 50
    assert latest.available_quantity == 80


def test_returns_allocated_batch():
    in_stock_batch = Batch("in-stock-123", "PRETTY-SOFA", 12, eta=None)
    shipment_batch = Batch("ship-1234", "PRETTY-SOFA", 24, eta=tomorrow)
    line = OrderLine("order-1123", "PRETTY-SOFA", 3)
    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raise_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("in-stock-123", "OFFICE-DIRECTOR-CHAIR", 20, eta=None)
    allocate(OrderLine("order-123", "OFFICE-DIRECTOR-CHAIR", 20), [batch])

    with pytest.raises(OutOfStock, match="OFFICE-DIRECTOR-CHAIR"):
        allocate(OrderLine("order-124", "OFFICE-DIRECTOR-CHAIR", 1), [batch])
