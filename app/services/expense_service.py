from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional
from sqlalchemy import func, extract, case
from sqlalchemy.orm import Session, joinedload
from app.models.expense import Expense
from app.models.category import Category


def create_expense(
    db: Session,
    user_id: int,
    amount: Decimal,
    description: Optional[str],
    expense_date: date,
    category_id: int,
) -> Expense:
    """Insert a new expense record."""
    expense = Expense(
        amount=amount,
        description=description,
        date=expense_date,
        category_id=category_id,
        user_id=user_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_expenses(
    db: Session,
    user_id: int,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_by: str = "date",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Expense], int]:
    """
    Retrieve expenses with filtering, sorting, and pagination.
    Uses JOIN with categories and filters out soft-deleted records.
    Returns (expenses_list, total_count).
    """
    query = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.user_id == user_id, Expense.deleted_at.is_(None))
    )

    # Apply filters
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    # Count before pagination
    total = query.count()

    # Apply sorting
    sort_column = {
        "date": Expense.date,
        "amount": Expense.amount,
        "category": Expense.category_id,
        "created": Expense.created_at,
    }.get(sort_by, Expense.date)

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    offset = (page - 1) * per_page
    expenses = query.offset(offset).limit(per_page).all()

    return expenses, total


def get_expense_by_id(db: Session, user_id: int, expense_id: int) -> Optional[Expense]:
    """Fetch a single expense by ID with ownership check (excludes soft-deleted)."""
    return (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(
            Expense.id == expense_id,
            Expense.user_id == user_id,
            Expense.deleted_at.is_(None),
        )
        .first()
    )


def update_expense(
    db: Session,
    user_id: int,
    expense_id: int,
    amount: Optional[Decimal] = None,
    description: Optional[str] = None,
    expense_date: Optional[date] = None,
    category_id: Optional[int] = None,
) -> Optional[Expense]:
    """Update an existing expense record."""
    expense = get_expense_by_id(db, user_id, expense_id)
    if not expense:
        return None

    if amount is not None:
        expense.amount = amount
    if description is not None:
        expense.description = description
    if expense_date is not None:
        expense.date = expense_date
    if category_id is not None:
        expense.category_id = category_id

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, user_id: int, expense_id: int) -> bool:
    """Soft-delete an expense by setting deleted_at timestamp."""
    expense = get_expense_by_id(db, user_id, expense_id)
    if not expense:
        return False
    expense.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


def restore_expense(db: Session, user_id: int, expense_id: int) -> bool:
    """Restore a soft-deleted expense."""
    expense = (
        db.query(Expense)
        .filter(
            Expense.id == expense_id,
            Expense.user_id == user_id,
            Expense.deleted_at.is_not(None),
        )
        .first()
    )
    if not expense:
        return False
    expense.deleted_at = None
    db.commit()
    return True


# ── Analytics Queries ──────────────────────────────────────────────────────


def get_total_spending(
    db: Session, user_id: int, start_date: date, end_date: date
) -> Decimal:
    """SUM of all expenses in date range (excludes soft-deleted)."""
    result = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
            Expense.deleted_at.is_(None),
        )
        .scalar()
    )
    return Decimal(str(result))


def get_expense_count(
    db: Session, user_id: int, start_date: date, end_date: date
) -> int:
    """COUNT of expenses in date range."""
    return (
        db.query(func.count(Expense.id))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
            Expense.deleted_at.is_(None),
        )
        .scalar()
    )


def get_spending_by_category(
    db: Session, user_id: int, start_date: date, end_date: date
) -> list[dict]:
    """
    Aggregate spending by category using GROUP BY and JOIN.
    Returns list of {category_name, icon, color, total, count}.
    """
    results = (
        db.query(
            Category.name,
            Category.icon,
            Category.color,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        .join(Category, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
            Expense.deleted_at.is_(None),
        )
        .group_by(Category.name, Category.icon, Category.color)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    return [
        {
            "category": r.name,
            "icon": r.icon,
            "color": r.color,
            "total": float(r.total),
            "count": r.count,
        }
        for r in results
    ]


def get_daily_spending_trend(
    db: Session, user_id: int, start_date: date, end_date: date
) -> list[dict]:
    """
    Daily spending totals for the date range.
    Uses GROUP BY on date column.
    """
    results = (
        db.query(
            Expense.date,
            func.sum(Expense.amount).label("total"),
        )
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
            Expense.deleted_at.is_(None),
        )
        .group_by(Expense.date)
        .order_by(Expense.date)
        .all()
    )
    return [
        {"date": r.date.isoformat(), "total": float(r.total)}
        for r in results
    ]


def get_monthly_comparison(db: Session, user_id: int, months: int = 6) -> list[dict]:
    """
    Monthly spending totals for the last N months.
    Uses EXTRACT for month/year and GROUP BY.
    """
    cutoff = date.today().replace(day=1) - timedelta(days=(months - 1) * 30)

    results = (
        db.query(
            extract("year", Expense.date).label("year"),
            extract("month", Expense.date).label("month"),
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        .filter(
            Expense.user_id == user_id,
            Expense.date >= cutoff,
            Expense.deleted_at.is_(None),
        )
        .group_by(
            extract("year", Expense.date),
            extract("month", Expense.date),
        )
        .order_by(
            extract("year", Expense.date),
            extract("month", Expense.date),
        )
        .all()
    )

    month_names = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    return [
        {
            "label": f"{month_names[int(r.month)]} {int(r.year)}",
            "total": float(r.total),
            "count": r.count,
        }
        for r in results
    ]


def get_top_expenses(
    db: Session, user_id: int, start_date: date, end_date: date, limit: int = 5
) -> list[Expense]:
    """Top N largest expenses in date range, sorted DESC by amount."""
    return (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
            Expense.deleted_at.is_(None),
        )
        .order_by(Expense.amount.desc())
        .limit(limit)
        .all()
    )
