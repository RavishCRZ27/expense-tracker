"""Admin dashboard routes — platform-wide analytics and user management."""

import json
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def admin_dashboard(
    request: Request,
    user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Admin analytics dashboard with platform-wide statistics."""
    stats = admin_service.get_platform_stats(db)
    spending_by_user = admin_service.get_spending_by_user(db)
    category_dist = admin_service.get_global_category_distribution(db)
    monthly_trend = admin_service.get_monthly_platform_trend(db)
    recent_activity = admin_service.get_recent_activity(db, limit=15)
    daily_signups = admin_service.get_daily_signups(db)

    return templates.TemplateResponse(request, "admin/index.html", {
        "user": user,
        "stats": stats,
        "spending_by_user": json.dumps(spending_by_user),
        "category_dist": json.dumps(category_dist),
        "monthly_trend": json.dumps(monthly_trend),
        "recent_activity": recent_activity,
        "daily_signups": json.dumps(daily_signups),
    })


@router.get("/users")
def admin_users(
    request: Request,
    user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Admin user management page."""
    users = admin_service.get_all_users_with_stats(db)
    stats = admin_service.get_platform_stats(db)

    return templates.TemplateResponse(request, "admin/users.html", {
        "user": user,
        "users_list": users,
        "stats": stats,
    })
