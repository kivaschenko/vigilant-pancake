from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_session
from app.presentation.order_endpoints import router as order_router


app = FastAPI()


@app.get("/")
async def read_root(session: AsyncSession = Depends(get_session)):
    result = await session.execute("SELECT 1")
    return {"Hello": "World", "result": result.scalar()}


app.include_router(order_router, prefix="/orders", tags=["orders"])
