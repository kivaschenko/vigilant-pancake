from fastapi import FastAPI
from src.presentation.order_endpoints import router as order_router
from src.infrastructure.database import SessionLocal
from src.infrastructure.repository import SQLAlchemyRepository
from src.application.order_service import OrderService

app = FastAPI()

# TODO: fix deprecated decorator, exchange with `lifespan`
@app.on_event("startup")
def startup_event():
    app.state.db = SessionLocal()

@app.on_event("shutdown")
def shutdown_event():
    app.state.db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(order_router, prefix="/orders", tags=["orders"])

def get_order_service():
    session = app.state.db
    repo = SQLAlchemyRepository(session)
    return OrderService(repo, session)