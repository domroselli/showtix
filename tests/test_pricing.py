from app.pricing import (
    Line, PriceBreakdown, PricingLine, Promo, discount, price_order, pricing_lines, service_fees, subtotal, tax,
)

LOCALS10 = Promo(code="LOCALS10", kind="percent", value=10)
WELCOME5 = Promo(code="WELCOME5", kind="fixed", value=500)


def test_subtotal_sums_qty_times_price():
    assert subtotal([Line(qty=2, unit_price_cents=12000), Line(qty=1, unit_price_cents=6900)]) == 30900


def test_service_fee_is_750_cents_per_ticket():
    assert service_fees(1) == 750
    assert service_fees(3) == 2250
    assert service_fees(8) == 6000


def test_tax_is_nine_percent():
    assert tax(6900) == 621
    assert tax(24000) == 2160


def test_tax_rounds_half_up_to_the_cent():
    assert tax(50) == 5  # 4.50 cents rounds up
    assert tax(49) == 4  # 4.41 cents rounds down
    assert tax(61) == 5  # 5.49 cents rounds down


def test_no_promo_means_no_discount():
    assert discount(24000, None) == 0


def test_percent_promo_discounts_the_subtotal():
    assert discount(24000, LOCALS10) == 2400


def test_percent_promo_rounds_half_up_to_the_cent():
    assert discount(6905, LOCALS10) == 691  # 690.5 cents


def test_percent_promo_cannot_exceed_the_subtotal():
    assert discount(5000, Promo(code="X", kind="percent", value=150)) == 5000


def test_fixed_promo_takes_a_flat_amount_off():
    assert discount(24000, WELCOME5) == 500


def test_fixed_promo_cannot_go_below_zero():
    assert discount(300, WELCOME5) == 300


def test_order_without_promo():
    breakdown = price_order([Line(qty=2, unit_price_cents=12000)])
    assert breakdown.subtotal_cents == 24000
    assert breakdown.discount_cents == 0
    assert breakdown.fees_cents == 1500
    assert breakdown.tax_cents == 2160
    assert breakdown.total_cents == 27660


def test_tax_never_applies_to_fees():
    breakdown = price_order([Line(qty=1, unit_price_cents=6900)])
    assert breakdown.tax_cents == 621
    assert breakdown.total_cents == 6900 + 750 + 621


def test_pricing_lines_list_the_breakdown_in_order():
    breakdown = PriceBreakdown(subtotal_cents=24000, discount_cents=0, fees_cents=1500, tax_cents=2160, total_cents=27660)
    assert pricing_lines(breakdown) == [
        PricingLine("Subtotal", 24000),
        PricingLine("Discount", 0),
        PricingLine("Service fees", 1500),
        PricingLine("Tax", 2160),
        PricingLine("Total", 27660),
    ]


def test_pricing_lines_name_the_promo_and_show_the_discount_as_negative():
    breakdown = PriceBreakdown(subtotal_cents=6900, discount_cents=500, fees_cents=750, tax_cents=576, total_cents=7726)
    assert pricing_lines(breakdown, "WELCOME5")[1] == PricingLine("Discount (WELCOME5)", -500)
