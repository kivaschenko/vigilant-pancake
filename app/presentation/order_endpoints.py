from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.infrastructure.database import get_session
from app.infrastructure.batch_repository import SQLAlchemyRepository
from app.application.order_service import OrderService, InvalidSku

router = APIRouter()


class BatchSchema(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: Optional[date]


class OrderLineSchema(BaseModel):
    orderid: str
    sku: str
    qty: int

def get_repository(session: AsyncSession):
    return SQLAlchemyRepository(session)

def get_order_service(session: AsyncSession = Depends(get_session)):
    repo = get_repository(session)
    return OrderService(repo, session)


print(get_order_service(), "get_order_service")


@router.post("/batches", status_code=status.HTTP_201_CREATED, tags=["orders"])
async def add_batch(
    batch: BatchSchema, service: OrderService = Depends(get_order_service)
):
    await service.add_batch(batch.ref, batch.sku, batch.qty, batch.eta)
    return {"message": "Batch added"}


@router.post(
    "/allocate",
    tags=["orders"],
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
)
async def allocate_order(
    line: OrderLineSchema, service: OrderService = Depends(get_order_service)
):
    try:
        batch_ref = await service.allocate(line.orderid, line.sku, line.qty)
        return {"batch_ref": batch_ref}
    except InvalidSku as e:
        raise HTTPException(status_code=400, detail=str(e))
