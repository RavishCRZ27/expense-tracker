from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.database import engine, Base, SessionLocal
from app.models import User, Category, Expense  # noqa: F401 — ensure models are registered
from app.services.category_service import seed_categories
from app.services.auth_service import seed_admin
from app.routers import auth, dashboard, expenses, api, admin

# ── OpenAPI Configuration ──────────────────────────────────────────────────

app = FastAPI(
    title="Personal Expense Tracker",
    description=(
        "A full-stack web application for tracking, categorizing, and analyzing "
        "personal expenses. Features JWT authentication, CRUD operations with "
        "soft-delete, and rich analytics dashboards.\n\n"
        "## Authentication\n"
        "All API endpoints require authentication via JWT stored in an HttpOnly cookie. "
        "Log in through the web UI at `/login` or use the `/api/v1/me` endpoint to verify.\n\n"
        "## Key Features\n"
        "- **Expense CRUD**: Create, read, update, and soft-delete expenses\n"
        "- **Filtering & Sorting**: Filter by category, date range; sort by date, amount\n"
        "- **Analytics**: Spending by category, daily trends, monthly comparisons\n"
        "- **Admin Panel**: Platform-wide analytics and user management\n"
        "- **Soft Delete**: Deleted expenses can be restored\n"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Static Files ───────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ── Routers ────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(expenses.router)
app.include_router(api.router)
app.include_router(admin.router)

# ── Startup Events ─────────────────────────────────────────────────────────


@app.on_event("startup")
def on_startup():
    """Create tables and seed default data on startup."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_categories(db)
        seed_admin(db)
    finally:
        db.close()
