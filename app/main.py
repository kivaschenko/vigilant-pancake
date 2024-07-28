from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.infrastructure.database import Database
from app.presentation.order_endpoints import router as order_router


# Initialize the database connection pool
@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.init()
    print("Database initialized")
    await Database.create_tables()
    try:
        yield
        print("Database closed")
    finally:
        await Database._pool.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root(db: Database = Depends(Database)):
    async with db._pool.acquire() as connection:
        result = await connection.execute("SELECT 1")
    return {"Hello": "World", "result": result}


# Include the order router
app.include_router(order_router, tags=["orders"])
