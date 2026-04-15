# Personal Expense Tracker

A full-stack web application for tracking, categorizing, and analyzing personal expenses. Built as a DBMS lab project demonstrating relational database design, SQL queries, and web application development.

## Tech Stack

- **Backend**: FastAPI (Python)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 16
- **Frontend**: Jinja2 Templates + Tailwind CSS v4
- **Charts**: Chart.js v4
- **Auth**: JWT (HttpOnly cookies)

## Features

- **User Authentication**: Register, login, logout with secure JWT tokens
- **Expense CRUD**: Create, read, update, and soft-delete expenses
- **Categories**: 8 predefined categories with emoji icons (Food, Travel, Shopping, Bills, Entertainment, Health, Education, Other)
- **Filtering & Sorting**: Filter by category, date range; sort by date, amount, category
- **Analytics Dashboard**: Summary cards, doughnut chart (category breakdown), line chart (daily trends), bar chart (monthly comparison)
- **REST API**: Full JSON API with OpenAPI/Swagger documentation at `/docs`
- **Soft Delete**: Deleted expenses can be restored

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16
- Node.js (for Tailwind CSS compilation)
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Setup

```bash
# 1. Clone and enter project
cd expense-tracker

# 2. Start PostgreSQL (if not running)
LC_ALL="C" pg_ctl -D /opt/homebrew/var/postgresql@16 start

# 3. Create database
createdb expense_db

# 4. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 5. Copy and configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 6. Run database migrations
alembic upgrade head

# 7. Install Tailwind CSS and build styles
npm install
npm run build:css

# 8. Start the application
uvicorn app.main:app --reload
```

### Access

- **Web App**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## Project Structure

```
expense-tracker/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy engine & session
│   ├── dependencies.py      # Auth dependencies
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py          # Users table
│   │   ├── category.py      # Categories table
│   │   └── expense.py       # Expenses table (with soft delete)
│   ├── schemas/             # Pydantic validation schemas
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py  # JWT & password hashing
│   │   ├── expense_service.py  # CRUD + analytics queries
│   │   └── category_service.py # Category management
│   ├── routers/             # Route handlers
│   │   ├── auth.py          # Login, register, logout
│   │   ├── dashboard.py     # Analytics dashboard
│   │   ├── expenses.py      # Expense CRUD pages
│   │   └── api.py           # REST API endpoints
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS & JS assets
├── alembic/                 # Database migrations
├── styles/                  # Tailwind CSS source
├── requirements.txt
└── package.json
```

## Database Schema

### ER Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   users     │     │   expenses   │     │ categories  │
├─────────────┤     ├──────────────┤     ├─────────────┤
│ id (PK)     │────<│ id (PK)      │>────│ id (PK)     │
│ username    │     │ amount       │     │ name        │
│ email       │     │ description  │     │ icon        │
│ hashed_pwd  │     │ date         │     │ color       │
│ full_name   │     │ category_id  │     └─────────────┘
│ created_at  │     │ user_id      │
└─────────────┘     │ created_at   │
                    │ updated_at   │
                    │ deleted_at   │
                    └──────────────┘
```

### Key SQL Queries Used

- **JOINs**: Expenses with categories for display
- **GROUP BY + Aggregation**: Spending by category, daily totals
- **EXTRACT**: Monthly/yearly breakdowns
- **Filtering**: Date ranges, category filtering
- **Soft Delete**: `WHERE deleted_at IS NULL`
- **Indexes**: Composite indexes on `(user_id, date)` and `(user_id, category_id)`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/me` | Current user profile |
| GET | `/api/v1/categories` | List all categories |
| GET | `/api/v1/expenses` | List expenses (filtered) |
| POST | `/api/v1/expenses` | Create expense |
| GET | `/api/v1/expenses/{id}` | Get single expense |
| PUT | `/api/v1/expenses/{id}` | Update expense |
| DELETE | `/api/v1/expenses/{id}` | Soft-delete expense |
| POST | `/api/v1/expenses/{id}/restore` | Restore deleted expense |
| GET | `/api/v1/dashboard/summary` | Analytics summary |

## License

MIT
