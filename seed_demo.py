"""
seed_demo.py — Inserts realistic mock users and expense data for demonstration.
Run once: python seed_demo.py

Creates:
  - 4 demo users with varied spending profiles
  - ~60 expenses spread across 4 months and all 8 categories
  - Realistic Indian rupee amounts

Safe to re-run: skips users that already exist by username.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from decimal import Decimal
import random
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.user import User
from app.models.expense import Expense

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Demo Users ─────────────────────────────────────────────────────────────

DEMO_USERS = [
    {
        "username": "alice",
        "email": "alice@demo.com",
        "full_name": "Alice Sharma",
        "password": "demo1234",
    },
    {
        "username": "bob",
        "email": "bob@demo.com",
        "full_name": "Bob Mehta",
        "password": "demo1234",
    },
    {
        "username": "carol",
        "email": "carol@demo.com",
        "full_name": "Carol Nair",
        "password": "demo1234",
    },
    {
        "username": "david",
        "email": "david@demo.com",
        "full_name": "David Rao",
        "password": "demo1234",
    },
]

# ── Expense Templates per Category ─────────────────────────────────────────
# (category_id, description, amount_range_min, amount_range_max)

EXPENSE_TEMPLATES = {
    1: [  # Food
        ("Swiggy order – Biryani",        180,  450),
        ("Zomato – Pizza",                220,  520),
        ("Groceries – D-Mart",            800, 2200),
        ("Office lunch",                  120,  280),
        ("Weekend brunch",                350,  900),
        ("Tea & snacks",                   40,  150),
        ("Restaurant dinner",             600, 1800),
    ],
    2: [  # Travel
        ("Ola cab – office commute",       80,  250),
        ("Uber – airport drop",           350,  900),
        ("Petrol refill",                1200, 2500),
        ("Bus pass – monthly",            500,  900),
        ("Train ticket – Mumbai local",    50,  120),
        ("Flight – Bangalore return",    4500, 9000),
        ("Metro card recharge",           200,  500),
    ],
    3: [  # Shopping
        ("Amazon – electronics",         1200, 8000),
        ("Myntra – clothing",             600, 3000),
        ("Flipkart – home essentials",    400, 2000),
        ("Local market – vegetables",     150,  400),
        ("Stationery – notebook & pens",   80,  350),
        ("Nike shoes",                   2500, 6000),
    ],
    4: [  # Bills
        ("Airtel mobile recharge",        239,  599),
        ("Electricity bill",              800, 2400),
        ("Netflix subscription",          199,  649),
        ("Spotify premium",               119,  119),
        ("Internet broadband bill",       499,  999),
        ("Gas cylinder",                  900, 1100),
    ],
    5: [  # Entertainment
        ("Movie – multiplex ticket",      200,  450),
        ("BookMyShow – concert",          500, 2500),
        ("Bowling & arcade",              400,  900),
        ("Gaming – Steam purchase",       300, 2000),
        ("Weekend getaway hotel",        2000, 6000),
    ],
    6: [  # Health
        ("Pharmacy – medicines",          150,  900),
        ("Apollo 24/7 consultation",      299,  699),
        ("Gym membership – monthly",      800, 2500),
        ("Blood test – lab",              400, 1200),
        ("Nutritional supplements",       600, 2000),
    ],
    7: [  # Education
        ("Udemy course",                  399,  699),
        ("Coursera subscription",         999, 1999),
        ("Books – technical",             350, 1200),
        ("College examination fee",       500, 2000),
        ("Tuition – monthly",            1500, 5000),
    ],
    8: [  # Other
        ("ATM withdrawal charges",         20,   50),
        ("Donation – local NGO",          200, 1000),
        ("Gift – birthday",               500, 3000),
        ("Laundry service",               150,  400),
        ("Miscellaneous repairs",         300, 2000),
    ],
}

# Distribution: how many expenses each user gets per category (roughly)
USER_CATEGORY_WEIGHTS = {
    "alice": {1: 7, 2: 3, 3: 5, 4: 4, 5: 2, 6: 2, 7: 3, 8: 1},  # foodie + shopper
    "bob":   {1: 4, 2: 6, 3: 3, 4: 4, 5: 3, 6: 2, 7: 2, 8: 2},  # traveller
    "carol": {1: 5, 2: 2, 3: 4, 4: 3, 5: 4, 6: 4, 7: 5, 8: 1},  # health + education
    "david": {1: 4, 2: 4, 3: 3, 4: 5, 5: 3, 6: 1, 7: 2, 8: 3},  # bills-heavy
}


def random_date_in_last_4_months() -> date:
    today = date.today()
    start = today - timedelta(days=120)
    delta = (today - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed():
    db = SessionLocal()
    created_users = []

    print("\n📦 Seeding demo users...")
    for u in DEMO_USERS:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if existing:
            print(f"  ⏭  Skipping '{u['username']}' (already exists)")
            created_users.append(existing)
            continue

        user = User(
            username=u["username"],
            email=u["email"],
            full_name=u["full_name"],
            hashed_password=pwd_ctx.hash(u["password"]),
            is_admin=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
        print(f"  ✅ Created user: {user.username} (id={user.id})")

    print("\n💸 Seeding expenses...")
    total_inserted = 0

    for user in created_users:
        weights = USER_CATEGORY_WEIGHTS.get(user.username, {})
        user_total = 0

        for cat_id, count in weights.items():
            templates = EXPENSE_TEMPLATES[cat_id]
            for _ in range(count):
                template = random.choice(templates)
                desc, min_amt, max_amt = template
                amount = Decimal(str(round(random.uniform(min_amt, max_amt), 2)))
                expense = Expense(
                    user_id=user.id,
                    category_id=cat_id,
                    amount=amount,
                    description=desc,
                    date=random_date_in_last_4_months(),
                )
                db.add(expense)
                user_total += float(amount)
                total_inserted += 1

        db.commit()
        print(f"  ✅ {user.username}: {sum(weights.values())} expenses  (≈ ₹{user_total:,.0f})")

    db.close()
    print(f"\n🎉 Done! {total_inserted} expenses inserted across {len(created_users)} users.")
    print("\nDemo credentials (all users):")
    print("  username: alice / bob / carol / david")
    print("  password: demo1234\n")


if __name__ == "__main__":
    seed()
