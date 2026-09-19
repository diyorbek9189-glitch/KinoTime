"""Kino kalendari — yaqin premyeralar (statik ro'yxat, vaqti-vaqti bilan yangilab turing).

Sanalar jahon premyeralari (taxminiy, o'zgarishi mumkin).
O'zbekcha dublyaj odatda 1-4 hafta kechikib chiqadi.
"""
from datetime import date

# (sana, nom, janr)
UPCOMING = [
    (date(2026, 9, 19), "Him", "Qo'rqinchli"),
    (date(2026, 9, 26), "One Battle After Another", "Jangari"),
    (date(2026, 9, 26), "The Strangers 2", "Qo'rqinchli"),
    (date(2026, 10, 9), "Aang: So'nggi havo bukuvchi", "Multfilm"),
    (date(2026, 10, 16), "Tron: Ares", "Fantastika"),
    (date(2026, 11, 6), "Now You See Me 3", "Sarguzasht"),
    (date(2026, 11, 25), "Zootopia 2 / Hayvonlar shahri 2", "Multfilm"),
    (date(2026, 12, 11), "Jumanji 3", "Sarguzasht"),
    (date(2026, 12, 18), "Avengers: Doomsday", "Action"),
    (date(2026, 12, 18), "Dune: 3-qism", "Fantastika"),
    (date(2026, 12, 23), "Shrek 5", "Multfilm"),
    (date(2027, 3, 19), "Sonic 4", "Sarguzasht"),
    (date(2027, 5, 28), "Star Wars: Starfighter", "Fantastika"),
    (date(2027, 6, 18), "Toy Story 5 (qayta prokat)", "Multfilm"),
    (date(2027, 10, 1), "The Batman 2", "Jangari"),
    (date(2027, 11, 24), "Frozen 3 / Muzlik yurti 3", "Multfilm"),
    (date(2027, 12, 17), "Avengers: Secret Wars", "Action"),
]


def get_today():
    t = date.today()
    return [(d, n, g) for d, n, g in UPCOMING if d == t]


def get_week():
    from datetime import timedelta
    t = date.today()
    end = t + timedelta(days=7)
    return [(d, n, g) for d, n, g in UPCOMING if t <= d <= end]


def get_month():
    t = date.today()
    return [(d, n, g) for d, n, g in UPCOMING if d.year == t.year and d.month == t.month]


def get_year(y: int):
    return [(d, n, g) for d, n, g in UPCOMING if d.year == y]


def fmt(rows) -> str:
    if not rows:
        return ""
    return "\n".join(f"🗓 {d.strftime('%d.%m.%Y')} — <b>{n}</b> ({g})" for d, n, g in rows)
