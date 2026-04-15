"""
REST API endpoints for the Personal Expense Tracker.
All endpoints return JSON and are documented via OpenAPI/Swagger.
Access the interactive docs at /docs (Swagger UI) or /redoc (ReDoc).
"""

from datetime import date
from decimal import Decimal
from typing import Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user_api
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseListResponse,
    DashboardSummary,
)
from app.schemas.category import CategoryResponse
from app.schemas.user import UserResponse
from app.services import expense_service, category_service
from datetime import timedelta

router = APIRouter(prefix="/api/v1", tags=["REST API"])


# ── User ───────────────────────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Returns the profile of the currently authenticated user.",
)
def api_get_me(user: User = Depends(get_current_user_api)):
    return user


# ── Categories ─────────────────────────────────────────────────────────────


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    summary="List all categories",
    description="Returns all available expense categories with their icons and colors.",
)
def api_list_categories(db: Session = Depends(get_db)):
    return category_service.get_all_categories(db)


# ── Expenses CRUD ──────────────────────────────────────────────────────────


@router.get(
    "/expenses",
    response_model=ExpenseListResponse,
    summary="List expenses",
    description=(
        "Retrieve the authenticated user's expenses with optional filtering by "
        "category and date range. Supports sorting and pagination."
    ),
)
def api_list_expenses(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    sort_by: str = Query("date", description="Sort field: date, amount, category, created"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db),
):
    expenses, total = expense_service.get_expenses(
        db, user.id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    return ExpenseListResponse(
        expenses=expenses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create expense",
    description="Create a new expense record for the authenticated user.",
)
def api_create_expense(
    data: ExpenseCreate,
    user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db),
):
    # Validate category exists
    cat = category_service.get_category_by_id(db, data.category_id)
    if not cat:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    expense = expense_service.create_expense(
        db, user.id, data.amount, data.description, data.date, data.category_id
    )
    # Reload with joined category
    return expense_service.get_expense_by_id(db, user.id, expense.id)


@router.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    summary="Get expense",
    description="Retrieve a single expense by ID (must belong to the authenticated user).",
)
def api_get_expense(
    expense_id: int,
    user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db),
):
    expense = expense_service.get_expense_by_id(db, user.id, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    summary="Update expense",
    description="Update fields of an existing expense. Only provided fields are updated.",
)
def api_update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db),
):
    if data.category_id:
        cat = category_service.get_category_by_id(db, data.category_id)
        if not cat:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    expense = expense_service.update_expense(
        db, user.id, expense_id,
        amount=data.amount,
        description=data.description,
        expense_date=data.date,
        category_id=data.category_id,
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.delete(
    "/expenses/{expense_id}",
    summary="Delete expense",
    description="Soft-delete an expense (sets deleted_at timestamp). Can be restored later.",
)
def api_delete_expense(
    expense_id: int,
    user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db),
):
    if not expense_service.delete_expense(db, user.id, expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"detail": "Expense deleted"}


@router.post(
    "/expenses/{expense_id}/restore",
    summary="Restore expense",
    description="Restore a previously soft-deleted expense.",
)
def api_restore_expense(
    expense_id: int,
    user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db),
):
    if not expense_service.restore_expense(db, user.id, expense_id):
        raise HTTPException(status_code=404, detail="Expense not found or not deleted")
    return {"detail": "Expense restored"}


# ── Dashboard Analytics ────────────────────────────────────────────────────


@router.get(
    "/dashboard/summary",
    response_model=DashboardSummary,
    summary="Dashboard summary",
    description=(
        "Get aggregated analytics including total spending, spending by category "
        "(with JOIN), daily trends, and monthly comparison for the specified period."
    ),
)
def api_dashboard_summary(
    period: str = Query("monthly", description="Period: daily, monthly, or yearly"),
    month: Optional[int] = Query(None, description="Month number (1-12)"),
    year: Optional[int] = Query(None, description="Year (e.g., 2026)"),
    user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db),
):
    today = date.today()
    if not year:
        year = today.year
    if not month:
        month = today.month

    if period == "daily":
        start_date = today
        end_date = today
    elif period == "yearly":
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
    else:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

    total_spending = expense_service.get_total_spending(db, user.id, start_date, end_date)
    expense_count = expense_service.get_expense_count(db, user.id, start_date, end_date)
    spending_by_category = expense_service.get_spending_by_category(db, user.id, start_date, end_date)
    daily_trend = expense_service.get_daily_spending_trend(db, user.id, start_date, end_date)
    monthly_comparison = expense_service.get_monthly_comparison(db, user.id, months=6)

    days_in_range = max((end_date - start_date).days + 1, 1)
    avg_daily = total_spending / days_in_range if total_spending else Decimal("0.00")

    top_category = spending_by_category[0]["category"] if spending_by_category else None

    return DashboardSummary(
        total_spending=total_spending,
        average_daily=round(avg_daily, 2),
        expense_count=expense_count,
        top_category=top_category,
        spending_by_category=spending_by_category,
        daily_trend=daily_trend,
        monthly_comparison=monthly_comparison,
    )
