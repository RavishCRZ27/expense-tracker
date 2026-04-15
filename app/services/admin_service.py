"""Admin analytics service — platform-wide queries across all users."""

from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func, extract, desc
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.expense import Expense
from app.models.category import Category


def get_platform_stats(db: Session) -> dict:
    """Get high-level platform statistics."""
    total_users = db.query(func.count(User.id)).scalar()
    total_expenses = (
        db.query(func.count(Expense.id))
        .filter(Expense.deleted_at.is_(None))
        .scalar()
    )
    total_spending = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.deleted_at.is_(None))
        .scalar()
    )

    # Active users in last 30 days (users who added expenses)
    cutoff = date.today() - timedelta(days=30)
    active_users = (
        db.query(func.count(func.distinct(Expense.user_id)))
        .filter(Expense.deleted_at.is_(None), Expense.date >= cutoff)
        .scalar()
    )

    return {
        "total_users": total_users,
        "total_expenses": total_expenses,
        "total_spending": float(Decimal(str(total_spending))),
        "active_users": active_users,
    }


def get_all_users_with_stats(db: Session) -> list[dict]:
    """Get all users with their expense statistics."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for user in users:
        expense_count = (
            db.query(func.count(Expense.id))
            .filter(Expense.user_id == user.id, Expense.deleted_at.is_(None))
            .scalar()
        )
        total_spent = (
            db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(Expense.user_id == user.id, Expense.deleted_at.is_(None))
            .scalar()
        )
        last_expense = (
            db.query(func.max(Expense.date))
            .filter(Expense.user_id == user.id, Expense.deleted_at.is_(None))
            .scalar()
        )
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "expense_count": expense_count,
            "total_spent": float(Decimal(str(total_spent))),
            "last_expense": last_expense,
        })
    return result


def get_spending_by_user(db: Session) -> list[dict]:
    """Aggregate total spending per user for comparison charts."""
    results = (
        db.query(
            User.username,
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
            func.count(Expense.id).label("count"),
        )
        .outerjoin(Expense, (Expense.user_id == User.id) & Expense.deleted_at.is_(None))
        .group_by(User.id, User.username)
        .order_by(desc("total"))
        .all()
    )
    return [
        {"username": r.username, "total": float(r.total), "count": r.count}
        for r in results
    ]


def get_global_category_distribution(db: Session) -> list[dict]:
    """Category spending distribution across all users."""
    results = (
        db.query(
            Category.name,
            Category.icon,
            Category.color,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        .join(Category, Expense.category_id == Category.id)
        .filter(Expense.deleted_at.is_(None))
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


def get_monthly_platform_trend(db: Session, months: int = 6) -> list[dict]:
    """Monthly total spending across the entire platform."""
    cutoff = date.today().replace(day=1) - timedelta(days=(months - 1) * 30)
    results = (
        db.query(
            extract("year", Expense.date).label("year"),
            extract("month", Expense.date).label("month"),
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
            func.count(func.distinct(Expense.user_id)).label("users"),
        )
        .filter(Expense.date >= cutoff, Expense.deleted_at.is_(None))
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
            "users": r.users,
        }
        for r in results
    ]


def get_recent_activity(db: Session, limit: int = 20) -> list:
    """Get the most recent expenses across all users."""
    return (
        db.query(Expense)
        .options(joinedload(Expense.category), joinedload(Expense.user))
        .filter(Expense.deleted_at.is_(None))
        .order_by(Expense.created_at.desc())
        .limit(limit)
        .all()
    )


def get_daily_signups(db: Session, days: int = 30) -> list[dict]:
    """Daily user registration count for the last N days."""
    cutoff = date.today() - timedelta(days=days)
    results = (
        db.query(
            func.date(User.created_at).label("day"),
            func.count(User.id).label("count"),
        )
        .filter(User.created_at >= cutoff)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )
    return [
        {"date": str(r.day), "count": r.count}
        for r in results
    ]
