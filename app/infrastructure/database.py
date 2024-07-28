import asyncpg
from contextlib import asynccontextmanager
from config import settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS "order_lines" (
  "id" SERIAL PRIMARY KEY,
  "sku" VARCHAR(255) NOT NULL,
  "qty" INT NOT NULL
);

CREATE TABLE IF NOT EXISTS "batches" (
  "id" SERIAL PRIMARY KEY,
  "reference" VARCHAR(255) NOT NULL,
  "sku" VARCHAR(255) NOT NULL,
  "_purchased_quantity" INT NOT NULL,
  "eta" DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS "allocations" (
  "id" SERIAL PRIMARY KEY,
  "orderline_id" INT NOT NULL,
  "batch_id" INT NOT NULL,
  FOREIGN KEY ("orderline_id") REFERENCES "order_lines" ("id"),
  FOREIGN KEY ("batch_id") REFERENCES "batches" ("id")
);
"""


class Database:
    _pool = None

    @classmethod
    async def init(cls):
        cls._pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
        print("pool", cls._pool.__repr__())

    @classmethod
    def release_connection(cls, connection):
        cls._pool.release(connection)
        print("connection released", connection)

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        connection = await cls._pool.acquire()
        print("connection", connection)
        try:
            yield connection
        finally:
            cls.release_connection(connection)
            print("connection released", connection)

    @classmethod
    async def create_tables(cls):
        print("Creating tables")
        async with cls.get_connection() as connection:
            await connection.execute(SCHEMA_SQL)
            print("Tables created successfully")
        print("Finished creating tables")
