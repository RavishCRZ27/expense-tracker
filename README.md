<div align="center">

# 💸 ExpenseTracker

### *Take control of your finances — beautifully.*

A production-quality, full-stack personal finance web application built on **FastAPI**, **PostgreSQL**, and **Tailwind CSS**. Features a public landing page, rich analytics dashboard, full REST API, and a protected admin panel with platform-wide insights.

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge)](https://www.sqlalchemy.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-Academic-blueviolet?style=for-the-badge)](./LICENSE)

</div>

---

## ✦ What is ExpenseTracker?

ExpenseTracker lets users **track every rupee they spend**, understand where their money goes with visual breakdowns, and make smarter financial decisions — all from a sleek, dark-themed web interface. 

Built as a **DBMS Lab Project**, it demonstrates real-world relational database design: normalized schemas, foreign key constraints, aggregate SQL queries, indexed lookups, soft-delete patterns, and Alembic-powered schema migrations.

---

## ✦ Key Features

| Feature | Description |
|---|---|
| 📊 **Analytics Dashboard** | Donut chart for category spend, daily trend line, 6-month comparison, and summary cards |
| 📝 **Full Expense CRUD** | Add, edit, filter, sort, and soft-delete expenses |
| 🏷️ **8 Preset Categories** | Food, Travel, Shopping, Bills, Entertainment, Health, Education, Others |
| 🔐 **Secure Auth** | JWT stored in HttpOnly cookies — no localStorage exposure |
| 🛡️ **Role-Based Access** | Admin role seeded at startup, protected via FastAPI dependency injection |
| 📡 **REST API** | Full JSON API with Swagger UI at `/docs` and ReDoc at `/redoc` |
| 🔍 **Filtering & Sorting** | Filter by category, date range; sort by amount, date, or category |
| ♻️ **Soft Delete** | Expenses use `deleted_at` timestamp — never permanently lost |
| 👨‍💼 **Admin Panel** | Platform-wide stats, cross-user spending charts, recent activity feed, user management |

---

## ✦ Tech Stack

| Layer | Technology |
|---|---|
| Backend | **FastAPI** (Python 3.12) |
| Database | **PostgreSQL 16** |
| ORM | **SQLAlchemy 2.0** (async-compatible) |
| Migrations | **Alembic** |
| Auth | **python-jose** (JWT) + **passlib/bcrypt** |
| Templating | **Jinja2** |
| Styling | **Tailwind CSS v4** |
| Charts | **Chart.js** |
| Validation | **Pydantic v2** |

---

## ✦ Project Structure

```
expense-tracker/
├── app/
│   ├── main.py               # App entrypoint — router registration & startup events
│   ├── config.py             # Environment config via Pydantic Settings
│   ├── database.py           # SQLAlchemy engine & session factory
│   ├── dependencies.py       # Reusable auth dependencies
│   ├── models/               # ORM models: User, Expense, Category
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # Business logic: expense, auth, category, admin
│   ├── routers/              # Route handlers: dashboard, expenses, auth, admin, api
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS, JS, images
├── alembic/                  # Database migration scripts
├── styles/                   # Tailwind CSS source (input.css)
├── docs/                     # Project documentation assets
├── report.md                 # DBMS concepts & architecture report
└── requirements.txt
```

---

## ✦ Getting Started

### Prerequisites

- **Python 3.12+**
- **PostgreSQL** running on port `5432`
- **Node.js** *(only needed to rebuild Tailwind CSS)*

### 1 — Clone

```bash
git clone https://github.com/RavishCRZ27/expense-tracker.git
cd expense-tracker
```

### 2 — Virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/expense_db
SECRET_KEY=your-super-secret-key-here
```

### 5 — Run migrations

```bash
alembic upgrade head
```

### 6 — Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

> App is live at **http://localhost:8000** 🚀

### 7 — (Optional) Rebuild CSS

```bash
npm run build:css
```

---

## ✦ Page Routes

| Route | Access | Description |
|---|---|---|
| `GET /` | Public | Landing page |
| `GET /login` | Public | Login page |
| `POST /login` | Public | Login form submission |
| `GET /register` | Public | Registration page |
| `POST /register` | Public | Registration form submission |
| `GET /logout` | Auth | Clears session, redirects to landing |
| `GET /dashboard` | Auth | Personal analytics dashboard |
| `GET /expenses` | Auth | Filterable & paginated expense list |
| `GET /expenses/add` | Auth | New expense form |
| `POST /expenses/add` | Auth | Submit new expense |
| `GET /expenses/{id}/edit` | Auth | Edit expense form |
| `POST /expenses/{id}/edit` | Auth | Submit expense update |
| `POST /expenses/{id}/delete` | Auth | Soft-delete an expense |
| `GET /admin` | **Admin** | Platform-wide analytics dashboard |
| `GET /admin/users` | **Admin** | User management table |

---

## ✦ REST API Reference

> Base URL: `/api/v1` · Auth: `Bearer <JWT>` header
> 
> Interactive docs → **[/docs](http://localhost:8000/docs)** (Swagger) · **[/redoc](http://localhost:8000/redoc)** (ReDoc)

### User

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/me` | Get authenticated user's profile |

### Categories

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/categories` | List all expense categories |

### Expenses

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/expenses` | List expenses *(filterable, sortable, paginated)* |
| `POST` | `/expenses` | Create a new expense |
| `GET` | `/expenses/{id}` | Get single expense by ID |
| `PUT` | `/expenses/{id}` | Update an expense |
| `DELETE` | `/expenses/{id}` | Soft-delete an expense |
| `POST` | `/expenses/{id}/restore` | Restore a soft-deleted expense |

**`GET /expenses` — Query Parameters**

| Param | Type | Default | Description |
|---|---|---|---|
| `category_id` | `int` | — | Filter by category |
| `start_date` | `date` | — | From date (`YYYY-MM-DD`) |
| `end_date` | `date` | — | To date (`YYYY-MM-DD`) |
| `sort_by` | `string` | `date` | `date` · `amount` · `category` · `created` |
| `sort_order` | `string` | `desc` | `asc` or `desc` |
| `page` | `int` | `1` | Page number |
| `per_page` | `int` | `20` | Items per page *(max 100)* |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard/summary` | Aggregated analytics: totals, category breakdown, trends |

**`GET /dashboard/summary` — Query Parameters**

| Param | Type | Default | Description |
|---|---|---|---|
| `period` | `string` | `monthly` | `daily` · `monthly` · `yearly` |
| `month` | `int` | current | Month (1–12) |
| `year` | `int` | current | Year (e.g. `2026`) |

---

## ✦ Database Design

The schema is normalized to **3NF** across three core tables:

- **`users`** — Auth credentials, role flag (`is_admin`), timestamps
- **`categories`** — Reusable lookup table (name, icon, color)
- **`expenses`** — Transaction records with `user_id` FK, `category_id` FK, and `deleted_at` for soft deletes

Indexes are placed on `expenses.date`, `expenses.user_id`, and unique constraints on `users.username` / `users.email`. See [`report.md`](./report.md) for the full DBMS analysis.

---

## ✦ Admin Panel

The admin account is automatically seeded at server startup via `auth_service.seed_admin()`. The admin role is enforced at the route level through a `get_current_admin` FastAPI dependency — any non-admin attempting to access `/admin` routes is redirected.

Admin capabilities:
- Platform-wide total users, expenses, and spending
- Spending-by-user bar chart *(LEFT OUTER JOIN with COALESCE)*
- Global category distribution donut chart
- Monthly platform spending trend
- Recent activity feed across all users
- Full user management table

---

<div align="center">
  <sub>Built with ❤️ as a DBMS Lab Project · 2026</sub>
</div>
