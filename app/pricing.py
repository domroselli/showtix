"""All money math lives here. Every amount is an integer number of cents.

Order of operations:
  1. Subtotal: sum of qty x tier price
  2. Discount: promo applied to the subtotal, never more than the subtotal
  3. Service fee: $7.50 per ticket, never discounted
  4. Tax: 9% of the discounted subtotal only, rounded half up once
  5. Total: discounted subtotal + fees + tax

Formatting: dollars() is the only place cents become "$250.44", for pages and prompts alike.
"""

from dataclasses import dataclass

SERVICE_FEE_CENTS = 750
TAX_RATE_PERCENT = 9


@dataclass(frozen=True)
class Promo:
    code: str
    kind: str  # "percent" (value = whole percent) or "fixed" (value = cents)
    value: int


@dataclass(frozen=True)
class Line:
    qty: int
    unit_price_cents: int


@dataclass(frozen=True)
class PriceBreakdown:
    subtotal_cents: int
    discount_cents: int
    fees_cents: int
    tax_cents: int
    total_cents: int


@dataclass(frozen=True)
class PricingLine:
    label: str
    amount_cents: int  # discounts are negative


def percent_of(amount_cents: int, percent: int) -> int:
    """percent% of amount, rounded half up to the cent, using integers only."""
    return (amount_cents * percent + 50) // 100


def line_total(qty: int, unit_price_cents: int) -> int:
    return qty * unit_price_cents


def subtotal(lines: list[Line]) -> int:
    return sum(line_total(line.qty, line.unit_price_cents) for line in lines)


def discount(subtotal_cents: int, promo: Promo | None) -> int:
    if promo is None:
        return 0
    if promo.kind == "percent":
        amount = percent_of(subtotal_cents, promo.value)
    else:
        amount = promo.value
    return min(amount, subtotal_cents)


def service_fees(ticket_count: int) -> int:
    return ticket_count * SERVICE_FEE_CENTS


def tax(taxable_cents: int) -> int:
    return percent_of(taxable_cents, TAX_RATE_PERCENT)


def price_order(lines: list[Line], promo: Promo | None = None) -> PriceBreakdown:
    subtotal_cents = subtotal(lines)
    discount_cents = discount(subtotal_cents, promo)
    discounted_cents = subtotal_cents - discount_cents
    fees_cents = service_fees(sum(line.qty for line in lines))
    tax_cents = tax(discounted_cents)
    return PriceBreakdown(
        subtotal_cents=subtotal_cents,
        discount_cents=discount_cents,
        fees_cents=fees_cents,
        tax_cents=tax_cents,
        total_cents=discounted_cents + fees_cents + tax_cents,
    )


def pricing_lines(breakdown: PriceBreakdown, promo_code: str | None = None) -> list[PricingLine]:
    """The breakdown as ordered lines for display, ending with the total."""
    return [
        PricingLine("Subtotal", breakdown.subtotal_cents),
        PricingLine(f"Discount ({promo_code})" if promo_code else "Discount", -breakdown.discount_cents),
        PricingLine("Service fees", breakdown.fees_cents),
        PricingLine("Tax", breakdown.tax_cents),
        PricingLine("Total", breakdown.total_cents),
    ]

def dollars(cents: int) -> str:
    """The only place cents become dollars, for pages and prompts alike: 25044 -> "$250.44"."""
    sign = "−" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100:,}.{cents % 100:02d}"
