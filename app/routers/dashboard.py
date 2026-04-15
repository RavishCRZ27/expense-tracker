from datetime import date, timedelta
from decimal import Decimal
import json
from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import expense_service, category_service

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request, user=Depends(get_current_user)):
    """Redirect home to dashboard."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/dashboard")
def dashboard(
    request: Request,
    period: str = Query("monthly", pattern="^(daily|monthly|yearly)$"),
    month: int = Query(None),
    year: int = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Main analytics dashboard with spending charts and summaries.
    Supports daily, monthly, and yearly views.
    """
    today = date.today()

    # Default to current month/year
    if not year:
        year = today.year
    if not month:
        month = today.month

    # Calculate date range based on period
    if period == "daily":
        start_date = today
        end_date = today
    elif period == "yearly":
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
    else:  # monthly
        start_date = date(year, month, 1)
        # Last day of month
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

    # Fetch analytics data using aggregate queries
    total_spending = expense_service.get_total_spending(db, user.id, start_date, end_date)
    expense_count = expense_service.get_expense_count(db, user.id, start_date, end_date)
    spending_by_category = expense_service.get_spending_by_category(db, user.id, start_date, end_date)
    daily_trend = expense_service.get_daily_spending_trend(db, user.id, start_date, end_date)
    monthly_comparison = expense_service.get_monthly_comparison(db, user.id, months=6)
    top_expenses = expense_service.get_top_expenses(db, user.id, start_date, end_date)

    # Calculate average daily spend
    days_in_range = max((end_date - start_date).days + 1, 1)
    avg_daily = total_spending / days_in_range if total_spending else Decimal("0.00")

    # Top category
    top_category = spending_by_category[0]["category"] if spending_by_category else None

    return templates.TemplateResponse(request, "dashboard/index.html", {
        "user": user,
        "period": period,
        "month": month,
        "year": year,
        "today": today,
        "start_date": start_date,
        "end_date": end_date,
        "total_spending": float(total_spending),
        "expense_count": expense_count,
        "avg_daily": float(round(avg_daily, 2)),
        "top_category": top_category,
        "spending_by_category": json.dumps(spending_by_category),
        "daily_trend": json.dumps(daily_trend),
        "monthly_comparison": json.dumps(monthly_comparison),
        "top_expenses": top_expenses,
    })
