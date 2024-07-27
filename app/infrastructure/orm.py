from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import registry

from app.domain import batch


metadata = MetaData()
mapper_registry = registry()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


# To avoid the ArgumentError indicating that the class OrderLine already has a primary
# mapper defined, you need to ensure that the start_mappers function is only called
# once and that the mappers are cleared properly after each test.
mappers_started = False


def start_mappers():
    global mappers_started
    if mappers_started:
        return
    lines_mapper = mapper_registry.map_imperatively(batch.OrderLine, order_lines)
    mapper_registry.map_imperatively(
        batch.Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
    mappers_started = True


def clear_mappers():
    mapper_registry.clear()
    global mappers_started
    mappers_started = False
