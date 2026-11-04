"""Server-rendered pages.

Routes read forms, call shows.py, orders.py and inventory.py, and render templates.
No business rules or money math here or in the templates; `dollars` (from pricing.py) only formats cents.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app import inventory, orders, shows
from app.clock import get_now
from app.db import get_db
from app.errors import BadRequest, ShowTixError
from app.models import CartItem, OrderRequest, QuoteRequest
from app.pricing import dollars

router = APIRouter(default_response_class=HTMLResponse, include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def showtime(starts_at: datetime) -> str:
    """2026-11-10T20:00 -> "Tue Nov 10, 8:00 PM" (no zero padding, works on every OS)."""
    hour = starts_at.hour % 12 or 12
    return f"{starts_at:%a %b} {starts_at.day}, {hour}:{starts_at:%M %p}"


templates.env.filters["dollars"] = dollars
templates.env.filters["showtime"] = showtime


def form_values(form) -> dict:
    """What the user typed, so the form can be refilled after a quote or an error."""
    return {
        "qty": {key.removeprefix("qty_"): value for key, value in form.items() if key.startswith("qty_")},
        "promo_code": form.get("promo_code", ""),
        "email": form.get("email", ""),
    }


def cart_items(form) -> list[CartItem]:
    items = []
    for key, value in form.items():
        if not key.startswith("qty_") or not value.strip():
            continue
        try:
            qty = int(value)
        except ValueError:
            raise BadRequest(f"Quantity must be a whole number, not {value!r}")
        if qty:
            items.append(CartItem(tier_id=int(key.removeprefix("qty_")), qty=qty))
    if not items:
        raise BadRequest("Choose at least one ticket")
    return items


def error_message(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        err = exc.errors()[0]
        if err["loc"] and err["loc"][0] == "email":
            return "Enter a valid email address"
        if "error" in err.get("ctx", {}):
            return str(err["ctx"]["error"])
        return err["msg"]
    return str(exc)


def performance_page(request, conn, performance_id, *, form=None, quote=None, error=None):
    return templates.TemplateResponse(
        request,
        "performance.html",
        {
            "show": shows.show_for_performance(conn, performance_id),
            "availability": inventory.availability(conn, performance_id),
            "form": form or {"qty": {}, "promo_code": "", "email": ""},
            "quote": quote,
            "error": error,
        },
        status_code=400 if error else 200,
    )


@router.get("/")
def index(request: Request, conn: sqlite3.Connection = Depends(get_db), now: datetime = Depends(get_now)):
    details = [shows.show_detail(conn, s.id, now) for s in shows.list_shows(conn)]
    return templates.TemplateResponse(request, "index.html", {"shows": details})


@router.get("/performances/{performance_id}")
def performance(request: Request, performance_id: int, conn: sqlite3.Connection = Depends(get_db)):
    return performance_page(request, conn, performance_id)


@router.post("/performances/{performance_id}/quote")
async def quote(
    request: Request,
    performance_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    now: datetime = Depends(get_now),
):
    form = await request.form()
    try:
        req = QuoteRequest(
            performance_id=performance_id,
            items=cart_items(form),
            promo_code=form.get("promo_code") or None,
        )
        q = orders.quote(conn, req, now)
    except (ShowTixError, ValidationError) as exc:
        return performance_page(request, conn, performance_id, form=form_values(form), error=error_message(exc))
    return performance_page(request, conn, performance_id, form=form_values(form), quote=q)


@router.post("/performances/{performance_id}/orders")
async def place_order(
    request: Request,
    performance_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    now: datetime = Depends(get_now),
):
    form = await request.form()
    try:
        req = OrderRequest(
            performance_id=performance_id,
            items=cart_items(form),
            promo_code=form.get("promo_code") or None,
            email=form.get("email", ""),
        )
        order = orders.create_order(conn, req, now)
    except (ShowTixError, ValidationError) as exc:
        return performance_page(request, conn, performance_id, form=form_values(form), error=error_message(exc))
    return RedirectResponse(f"/orders/{order.id}", status_code=303)


@router.get("/orders/{order_id}")
def order_page(request: Request, order_id: int, conn: sqlite3.Connection = Depends(get_db)):
    order = orders.get_order(conn, order_id)
    return templates.TemplateResponse(
        request,
        "order.html",
        {"order": order, "show": shows.show_for_performance(conn, order.performance_id)},
    )
