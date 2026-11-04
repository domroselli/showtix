# Seed data

Everything the app starts with: the shows, nights, prices, seats, promo codes and orders that `uv run python -m app.seed` creates. The tests use the same data, in a fresh in-memory database for every test. Use this page to work out your answer key.

The source is `app/seed.py`. If it and this page ever disagree, `app/seed.py` wins.

## Shows

Every show plays every night from **Nov 10 to Nov 23, 2026** (14 nights), at the same curtain time. 2 shows per category.

| Show id | Title | Category | Venue | Curtain | Performance ids (Nov 10 → Nov 23) |
| --- | --- | --- | --- | --- | --- |
| 1 | The Vanishing Ace | magic | Desert Bloom Theater | 7:00 PM | 1 → 14 |
| 2 | Smoke & Sleight | magic | Neon Mesa Showroom | 9:30 PM | 15 → 28 |
| 3 | Laugh Lines Live | comedy | Neon Mesa Showroom | 8:00 PM | 29 → 42 |
| 4 | Stand-Up Saloon | comedy | Desert Bloom Theater | 9:30 PM | 43 → 56 |
| 5 | Neon Nights Revue | music | Silver Coyote Hall | 8:00 PM | 57 → 70 |
| 6 | Desert Strings | music | Desert Bloom Theater | 7:30 PM | 71 → 84 |
| 7 | Skyline Circus | acrobatics | Silver Coyote Hall | 7:00 PM | 85 → 98 |
| 8 | Gravity Optional | acrobatics | Silver Coyote Hall | 8:00 PM | 99 → 112 |

Performance ids run in order by night: for example, Laugh Lines Live on Nov 12 is performance 31. `GET /shows/{show_id}` lists a show's performances with their ids.

`GET /shows` lists shows by title. With `start_date` and `end_date`, it lists shows with at least one performance in that range, both dates included.

## Price tiers and seats

Every performance has the same three tiers. Seats depend on the venue.

| Venue | Capacity | GA seats | Premium seats | VIP seats |
| --- | --- | --- | --- | --- |
| Desert Bloom Theater | 900 | 540 | 270 | 90 |
| Neon Mesa Showroom | 600 | 360 | 180 | 60 |
| Silver Coyote Hall | 1200 | 720 | 360 | 120 |

| Tier | Price | In cents |
| --- | --- | --- |
| GA | $69.00 | `6900` |
| Premium | $120.00 | `12000` |
| VIP | $199.99 | `19999` |

Tier ids run in order too: each performance's GA, Premium, VIP. `GET /performances/{id}/availability` shows a performance's tiers with their ids and seats left.

## The nearly sold-out tier

**Gravity Optional, Nov 14, VIP** is the one tier that's almost gone: 24 seats, 22 sold, **2 left**. Performance id 103, tier id 309. Every other tier has all its seats.

## Orders

The seed creates 3 paid orders, all on that tier, so **the first order you place is #4**.

| Order | Email | Tickets | Subtotal | Fees | Tax | Total |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | group1@example.com | 8 × VIP | `159992` | `6000` | `14399` | `180391` ($1,803.91) |
| 2 | group2@example.com | 8 × VIP | `159992` | `6000` | `14399` | `180391` ($1,803.91) |
| 3 | group3@example.com | 6 × VIP | `119994` | `4500` | `10799` | `135293` ($1,352.93) |

## Promo codes

| Code | Discount | Valid from | Valid to | Max uses | Used |
| --- | --- | --- | --- | --- | --- |
| `LOCALS10` | 10% off the subtotal | 2026-01-01 | 2027-12-31 | 500 | 0 |
| `SPRING24` | 20% off the subtotal | 2024-03-01 | 2024-05-31 | 200 | 0 |
| `WELCOME5` | $5.00 off the subtotal | 2026-01-01 | 2027-12-31 | 1000 | 0 |

Codes are matched without regard to case or surrounding spaces. `SPRING24` has expired, so using it gets a 400.

## How a price is built

All in integer cents, in this order (`app/pricing.py`):

1. **Subtotal:** qty × tier price, summed over the lines.
2. **Discount:** the promo, applied to the subtotal, never more than the subtotal.
3. **Service fee:** $7.50 per ticket, never discounted.
4. **Tax:** 9% of the subtotal after the discount (not the fees), rounded half up to the cent.
5. **Total:** discounted subtotal + fees + tax.

For example, 2 GA with no promo: subtotal `13800`, fees `1500`, tax `1242` (9% of 13800), total `16542` ($165.42).

An order can have at most 8 tickets.

## What time it is

- **In tests:** every test starts at **Nov 1, 2026, 12:00 PM**, before the first show, so every performance is upcoming and the live promo codes are valid. A test can change that (`tests/conftest.py`).
- **In the running app:** the real time in Las Vegas. Performances that have already started drop off a show's list.

_Generated from `app/seed.py`._
