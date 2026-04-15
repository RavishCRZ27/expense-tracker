from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import expense_service, category_service
import math

router = APIRouter(prefix="/expenses", tags=["Expenses"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def expense_list(
    request: Request,
    category_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    sort_by: str = Query("date"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Render the expense list page with filters, sorting, and pagination."""
    # Parse date strings
    parsed_start = None
    parsed_end = None
    if start_date:
        try:
            parsed_start = date.fromisoformat(start_date)
        except ValueError:
            pass
    if end_date:
        try:
            parsed_end = date.fromisoformat(end_date)
        except ValueError:
            pass

    per_page = 15
    expenses, total = expense_service.get_expenses(
        db,
        user.id,
        category_id=category_id,
        start_date=parsed_start,
        end_date=parsed_end,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )

    total_pages = math.ceil(total / per_page) if total > 0 else 1
    categories = category_service.get_all_categories(db)

    return templates.TemplateResponse(request, "expenses/list.html", {
        "user": user,
        "expenses": expenses,
        "categories": categories,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "category_id": category_id,
        "start_date": start_date or "",
        "end_date": end_date or "",
        "sort_by": sort_by,
        "sort_order": sort_order,
    })


@router.get("/add")
def add_expense_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Render the add expense form."""
    categories = category_service.get_all_categories(db)
    return templates.TemplateResponse(request, "expenses/create.html", {
        "user": user,
        "categories": categories,
        "error": None,
        "today": date.today().isoformat(),
    })


@router.post("/add")
def add_expense(
    request: Request,
    amount: str = Form(...),
    description: str = Form(None),
    expense_date: str = Form(...),
    category_id: int = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process the add expense form."""
    categories = category_service.get_all_categories(db)

    try:
        parsed_amount = Decimal(amount)
        if parsed_amount <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, ArithmeticError):
        return templates.TemplateResponse(request, "expenses/create.html", {
            "user": user,
            "categories": categories,
            "error": "Please enter a valid positive amount",
            "today": date.today().isoformat(),
        }, status_code=400)

    try:
        parsed_date = date.fromisoformat(expense_date)
    except ValueError:
        return templates.TemplateResponse(request, "expenses/create.html", {
            "user": user,
            "categories": categories,
            "error": "Please enter a valid date",
            "today": date.today().isoformat(),
        }, status_code=400)

    expense_service.create_expense(
        db, user.id, parsed_amount, description, parsed_date, category_id
    )
    return RedirectResponse(url="/expenses", status_code=302)


@router.get("/{expense_id}/edit")
def edit_expense_page(
    expense_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Render the edit expense form."""
    expense = expense_service.get_expense_by_id(db, user.id, expense_id)
    if not expense:
        return RedirectResponse(url="/expenses", status_code=302)

    categories = category_service.get_all_categories(db)
    return templates.TemplateResponse(request, "expenses/edit.html", {
        "user": user,
        "expense": expense,
        "categories": categories,
        "error": None,
    })


@router.post("/{expense_id}/edit")
def edit_expense(
    expense_id: int,
    request: Request,
    amount: str = Form(...),
    description: str = Form(None),
    expense_date: str = Form(...),
    category_id: int = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process the edit expense form."""
    try:
        parsed_amount = Decimal(amount)
        parsed_date = date.fromisoformat(expense_date)
    except (ValueError, ArithmeticError):
        expense = expense_service.get_expense_by_id(db, user.id, expense_id)
        categories = category_service.get_all_categories(db)
        return templates.TemplateResponse(request, "expenses/edit.html", {
            "user": user,
            "expense": expense,
            "categories": categories,
            "error": "Invalid amount or date",
        }, status_code=400)

    expense_service.update_expense(
        db, user.id, expense_id,
        amount=parsed_amount,
        description=description,
        expense_date=parsed_date,
        category_id=category_id,
    )
    return RedirectResponse(url="/expenses", status_code=302)


@router.post("/{expense_id}/delete")
def delete_expense(
    expense_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete an expense and redirect to list."""
    expense_service.delete_expense(db, user.id, expense_id)
    return RedirectResponse(url="/expenses", status_code=302)
