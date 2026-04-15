from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import (
    authenticate_user,
    create_user,
    create_access_token,
    get_user_by_username,
    get_user_by_email,
)
from app.dependencies import get_current_user_optional

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
def login_page(request: Request, user=Depends(get_current_user_optional)):
    """Render the login page. Redirect to dashboard if already logged in."""
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html", {
        "error": None,
    })


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Process login form submission."""
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(request, "auth/login.html", {
            "error": "Invalid username or password",
        }, status_code=400)

    token = create_access_token(data={"sub": str(user.id)})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
    )
    return response


@router.get("/register")
def register_page(request: Request, user=Depends(get_current_user_optional)):
    """Render the registration page."""
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth/register.html", {
        "error": None,
    })


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db),
):
    """Process registration form submission."""
    # Validation
    if password != confirm_password:
        return templates.TemplateResponse(request, "auth/register.html", {
            "error": "Passwords do not match",
        }, status_code=400)

    if len(password) < 6:
        return templates.TemplateResponse(request, "auth/register.html", {
            "error": "Password must be at least 6 characters",
        }, status_code=400)

    if get_user_by_username(db, username):
        return templates.TemplateResponse(request, "auth/register.html", {
            "error": "Username already taken",
        }, status_code=400)

    if get_user_by_email(db, email):
        return templates.TemplateResponse(request, "auth/register.html", {
            "error": "Email already registered",
        }, status_code=400)

    user = create_user(db, username, email, password, full_name)
    token = create_access_token(data={"sub": str(user.id)})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
    )
    return response


@router.get("/logout")
def logout():
    """Clear the auth cookie and redirect to login."""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
