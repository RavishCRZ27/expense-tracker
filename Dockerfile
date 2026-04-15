# ── Stage 1: Build Tailwind CSS ────────────────────────────────────────────
FROM node:22-alpine AS css-builder

WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY styles/ ./styles/
COPY app/templates/ ./app/templates/
RUN npx @tailwindcss/cli -i ./styles/input.css -o ./output.css --minify

# ── Stage 2: Python App ───────────────────────────────────────────────────
FROM python:3.12-slim

# Prevent .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY seed_demo.py .

# Copy compiled CSS from builder stage
COPY --from=css-builder /build/output.css ./app/static/css/output.css

# Expose port
EXPOSE 8000

# Run Alembic migrations, then start Uvicorn
# PORT env var is set by Render; falls back to 8000 locally
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
