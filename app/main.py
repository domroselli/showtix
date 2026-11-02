"""JSON API routes only. Business rules live in the modules they call. Web pages are in web.py."""

import sqlite3
from contextlib import asynccontextmanager
from datetime import date, datetime

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app import db, inventory, orders, seed, shows, web
from app.clock import get_now
from app.db import get_db
from app.errors import ShowTixError
from app.models import Availability, Order, OrderRequest, Quote, QuoteRequest, ShowDetail, ShowSummary


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not db.DB_PATH.exists():
        seed.reset_db()
    yield


app = FastAPI(title="ShowTix", lifespan=lifespan)
app.include_router(web.router)


@app.exception_handler(ShowTixError)
def handle_showtix_error(request: Request, exc: ShowTixError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.get("/shows")
def list_shows(
    start_date: date | None = None,
    end_date: date | None = None,
    conn: sqlite3.Connection = Depends(get_db),
) -> list[ShowSummary]:
    return shows.list_shows(conn, start_date, end_date)


@app.get("/shows/{show_id}")
def show_detail(
    show_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    now: datetime = Depends(get_now),
) -> ShowDetail:
    return shows.show_detail(conn, show_id, now)


@app.get("/performances/{performance_id}/availability")
def availability(performance_id: int, conn: sqlite3.Connection = Depends(get_db)) -> Availability:
    return inventory.availability(conn, performance_id)


@app.post("/orders/quote")
def quote(
    req: QuoteRequest,
    conn: sqlite3.Connection = Depends(get_db),
    now: datetime = Depends(get_now),
) -> Quote:
    return orders.quote(conn, req, now)


@app.post("/orders", status_code=201)
def create_order(
    req: OrderRequest,
    conn: sqlite3.Connection = Depends(get_db),
    now: datetime = Depends(get_now),
) -> Order:
    return orders.create_order(conn, req, now)


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, conn: sqlite3.Connection = Depends(get_db)) -> Order:
    return orders.cancel_order(conn, order_id)
