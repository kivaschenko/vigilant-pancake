import asyncpg
from fastapi import APIRouter, Depends, status, HTTPException
from app.infrastructure.database import Database
from app.infrastructure.batch_repository import AsyncpgRepository
from app.application.order_service import OrderService
from pydantic import BaseModel
from typing import List

router = APIRouter()


class BatchSchema(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: str


def get_repository(connection: asyncpg.Connection = Depends(Database.get_connection)):
    return AsyncpgRepository(connection)


def get_order_service(
    connection: asyncpg.Connection = Depends(Database.get_connection),
):
    repo = get_repository(connection)
    return OrderService(repo, connection)


@router.post("/batches", status_code=status.HTTP_201_CREATED, tags=["orders"])
async def add_batch(
    batch: BatchSchema, service: OrderService = Depends(get_order_service)
):
    await service.add_batch(batch.ref, batch.sku, batch.qty, batch.eta)
    return {"message": "Batch added"}


@router.get("/batches/{ref}", response_model=BatchSchema, tags=["orders"])
async def get_batch(ref: str, service: OrderService = Depends(get_order_service)):
    batch = await service.get_batch(ref)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.get("/batches", response_model=List[BatchSchema], tags=["orders"])
async def list_batches(service: OrderService = Depends(get_order_service)):
    return await service.list_batches()


@router.put("/batches/{ref}", tags=["orders"])
async def update_batch(
    ref: str, batch: BatchSchema, service: OrderService = Depends(get_order_service)
):
    await service.update_batch(ref, sku=batch.sku, qty=batch.qty, eta=batch.eta)
    return {"message": "Batch updated"}


@router.delete("/batches/{ref}", tags=["orders"])
async def delete_batch(ref: str, service: OrderService = Depends(get_order_service)):
    await service.delete_batch(ref)
    return {"message": "Batch deleted"}
