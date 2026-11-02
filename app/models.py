"""Pydantic models for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

MAX_TICKETS_PER_ORDER = 8


class CartItem(BaseModel):
    tier_id: int
    qty: int = Field(ge=1)


class QuoteRequest(BaseModel):
    performance_id: int
    items: list[CartItem] = Field(min_length=1)
    promo_code: str | None = None

    @model_validator(mode="after")
    def check_ticket_limit(self):
        tickets = sum(item.qty for item in self.items)
        if tickets > MAX_TICKETS_PER_ORDER:
            raise ValueError(
                f"An order can have at most {MAX_TICKETS_PER_ORDER} tickets; this one has {tickets}"
            )
        return self


class OrderRequest(QuoteRequest):
    email: str = Field(min_length=3, pattern=r".+@.+")


class QuoteLine(BaseModel):
    tier_id: int
    tier_name: str
    qty: int
    unit_price_cents: int
    line_total_cents: int


class PricingLine(BaseModel):
    label: str
    amount_cents: int


class Breakdown(BaseModel):
    lines: list[QuoteLine]
    pricing_lines: list[PricingLine]
    subtotal_cents: int
    discount_cents: int
    fees_cents: int
    tax_cents: int
    total_cents: int


class Quote(Breakdown):
    performance_id: int
    promo_code: str | None


class Order(Breakdown):
    id: int
    email: str
    performance_id: int
    status: str
    promo_code: str | None
    created_at: datetime


class TierAvailability(BaseModel):
    tier_id: int
    name: str
    price_cents: int
    seats_total: int
    seats_sold: int
    seats_left: int


class Availability(BaseModel):
    performance_id: int
    starts_at: datetime
    tiers: list[TierAvailability]


class ShowSummary(BaseModel):
    id: int
    title: str
    category: str
    venue: str


class Performance(BaseModel):
    id: int
    starts_at: datetime


class ShowDetail(ShowSummary):
    performances: list[Performance]
