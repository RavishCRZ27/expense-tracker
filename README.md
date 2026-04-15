<div align="center">
  <img src="./app/static/images/hero_abstract.png" alt="ExpenseTracker Banner" width="100%" />
</div>

<br/>

<div align="center">
  <h1>ExpenseTracker</h1>
  <p><strong>A full-stack personal finance management application built with FastAPI & PostgreSQL.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white" />
    <img src="https://img.shields.io/badge/PostgreSQL-16-316192?style=flat&logo=postgresql&logoColor=white" />
    <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat" />
    <img src="https://img.shields.io/badge/Alembic-Migrations-6BA81E?style=flat" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=flat&logo=tailwind-css&logoColor=white" />
    <img src="https://img.shields.io/badge/JWT-Auth-000000?style=flat&logo=jsonwebtokens&logoColor=white" />
  </p>
</div>

---

## Overview

ExpenseTracker is a production-quality web application that allows users to log, categorize, and analyze their personal expenses. It features a public landing page, a user-facing analytics dashboard with interactive charts, a full JSON REST API, and a protected admin panel with platform-wide insights.

The project was developed as a DBMS lab submission — demonstrating normalized schema design, complex SQL aggregation queries, relational joins, indexing strategies, schema versioning via Alembic, and soft-delete patterns on top of PostgreSQL.

<div align="center">
  <br/>
  <img src="./app/static/images/lifestyle.png" width="80%" style="border-radius: 12px" />
  <br/><br/>
</div>

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | FastAPI (Python 3.12) |
| **Database** | PostgreSQL 16 |
| **ORM** | SQLAlchemy 2.0 |
| **Schema Migrations** | Alembic |
| **Authentication** | JWT via `python-jose`, stored in HttpOnly cookies |
| **Password Hashing** | Passlib + bcrypt |
| **Templating** | Jinja2 |
| **Styling** | Tailwind CSS v4 |
| **Charts** | Chart.js |

---

## Project Structure

```
expense-tracker/
├── app/
│   ├── main.py               # App entrypoint, router registration, startup events
│   ├── config.py             # Environment settings (Pydantic Settings)
│   ├── database.py           # SQLAlchemy engine & session factory
│   ├── dependencies.py       # Auth dependencies (get_current_user, get_current_admin)
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── expense.py
│   │   └── category.py
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # Business logic layer
│   │   ├── expense_service.py
│   │   ├── auth_service.py
│   │   ├── category_service.py
│   │   └── admin_service.py
│   ├── routers/              # Route handlers
│   │   ├── dashboard.py
│   │   ├── expenses.py
│   │   ├── auth.py
│   │   ├── admin.py
│   │   └── api.py
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS, JS, images
├── alembic/                  # Database migration scripts
├── styles/                   # Tailwind CSS source
├── docs/                     # Project documentation assets
├── report.md                 # DBMS concepts report
└── requirements.txt
```

---

## Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL running locally on port `5432`
- Node.js (only required for rebuilding Tailwind CSS)

### 1. Clone the repository
```bash
git clone https://github.com/RavishCRZ27/expense-tracker.git
cd expense-tracker
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root (or update `app/config.py`):
```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/expense_db
SECRET_KEY=your-secret-key-here
```

### 5. Apply database migrations
```bash
alembic upgrade head
```

### 6. Run the development server
```bash
uvicorn app.main:app --reload --port 8000
```

The app will be available at **http://localhost:8000**.

### 7. (Optional) Rebuild Tailwind CSS
```bash
npm run build:css
```

---

## Page Routes

| Route | Auth Required | Description |
|---|---|---|
| `GET /` | No | Public landing page |
| `GET /login` | No | Login page |
| `POST /login` | No | Login form submission |
| `GET /register` | No | Registration page |
| `POST /register` | No | Registration form submission |
| `GET /logout` | Yes | Clears session cookie and redirects |
| `GET /dashboard` | Yes | Personal analytics dashboard |
| `GET /expenses` | Yes | Paginated, filterable expense list |
| `GET /expenses/add` | Yes | Add new expense form |
| `POST /expenses/add` | Yes | Submit new expense |
| `GET /expenses/{id}/edit` | Yes | Edit expense form |
| `POST /expenses/{id}/edit` | Yes | Submit expense edit |
| `POST /expenses/{id}/delete` | Yes | Soft-delete an expense |
| `GET /admin` | Admin Only | Admin analytics dashboard |
| `GET /admin/users` | Admin Only | Platform user management |

---

## REST API Endpoints

All API routes are prefixed with `/api/v1`. Authentication uses a Bearer token via the `Authorization` header (`Bearer <JWT>`). Interactive documentation is available at **`/docs`** (Swagger UI) and **`/redoc`**.

### User

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/me` | Returns the authenticated user's profile |

### Categories

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/categories` | Lists all available expense categories |

### Expenses

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/expenses` | List expenses with filtering, sorting & pagination |
| `POST` | `/api/v1/expenses` | Create a new expense |
| `GET` | `/api/v1/expenses/{id}` | Get a single expense by ID |
| `PUT` | `/api/v1/expenses/{id}` | Update an existing expense |
| `DELETE` | `/api/v1/expenses/{id}` | Soft-delete an expense |
| `POST` | `/api/v1/expenses/{id}/restore` | Restore a soft-deleted expense |

#### `GET /api/v1/expenses` — Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `category_id` | `int` | — | Filter by category |
| `start_date` | `date` | — | Filter from date (`YYYY-MM-DD`) |
| `end_date` | `date` | — | Filter to date (`YYYY-MM-DD`) |
| `sort_by` | `string` | `date` | Field to sort by: `date`, `amount`, `category`, `created` |
| `sort_order` | `string` | `desc` | `asc` or `desc` |
| `page` | `int` | `1` | Page number |
| `per_page` | `int` | `20` | Results per page (max 100) |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/dashboard/summary` | Aggregated analytics: total spend, category breakdown, daily trends, monthly comparison |

#### `GET /api/v1/dashboard/summary` — Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `period` | `string` | `monthly` | `daily`, `monthly`, or `yearly` |
| `month` | `int` | current | Month number (1–12) |
| `year` | `int` | current | Year (e.g. `2026`) |

---

## Features

- 📊 **Interactive Dashboard** — Spending by category (donut chart), daily trends, monthly comparison, and summary stats
- 🏷️ **8 Preset Categories** — Food, Travel, Shopping, Bills, Entertainment, Health, Education, Others
- 🔍 **Filtering & Sorting** — Filter by category and date range, sort by amount, date, or category
- 🔐 **JWT Authentication** — Secure, HttpOnly cookie-based sessions
- 🛡️ **Role-Based Access** — Admin role with `is_admin` DB flag and protected route dependency
- 📡 **REST API** — Full CRUD API with OpenAPI/Swagger documentation at `/docs`
- 🗑️ **Soft Delete** — Expenses are never hard-deleted; `deleted_at` timestamp approach
- 📈 **Admin Analytics** — Platform-wide stats: cross-user spending, global category distribution, recent activity feed
- 🔄 **Alembic Migrations** — Full schema version control

---

## License

This project is intended for academic and educational purposes.
