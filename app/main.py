from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.infrastructure.database import get_session
from app.infrastructure.orm import start_mappers
from app.presentation.order_endpoints import router as order_router


app = FastAPI()

# Ensure mappers are started before any database operations
start_mappers()

@app.get("/")
async def read_root(session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT 1"))
    return {"Hello": "World", "result": result.scalar()}

# Include the order router
app.include_router(order_router, prefix="/orders", tags=["orders"])
