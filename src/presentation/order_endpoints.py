from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from datetime import date
from src.infrastructure.database import SessionLocal, get_repository
from src.application.order_service import OrderService, InvalidSku

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


def get_order_service(session = Depends(SessionLocal), repo = Depends(get_repository)):
    return OrderService(repo, session)



@router.post("/batches", status_code=201, tags=["orders"])
def add_batch(batch: BatchSchema, service: OrderService = Depends(get_order_service)):
    service.add_batch(batch.ref, batch.sku, batch.qty, batch.eta)
    return {"message": "Batch added"}

@router.post("/allocate", tags=["orders"])
def allocate_order(line: OrderLineSchema, service: OrderService = Depends(get_order_service)):
    try:
        batch_ref = service.allocate(line.orderid, line.sku, line.qty)
        return {"batch_ref": batch_ref}
    except InvalidSku as e:
        raise HTTPException(status_code=400, detail=str(e))