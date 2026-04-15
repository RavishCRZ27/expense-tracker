from sqlalchemy.orm import Session
from app.models.category import Category


# Default categories to seed
DEFAULT_CATEGORIES = [
    {"name": "Food", "icon": "🍔", "color": "#f97316"},
    {"name": "Travel", "icon": "✈️", "color": "#3b82f6"},
    {"name": "Shopping", "icon": "🛍️", "color": "#ec4899"},
    {"name": "Bills", "icon": "📄", "color": "#ef4444"},
    {"name": "Entertainment", "icon": "🎬", "color": "#8b5cf6"},
    {"name": "Health", "icon": "💊", "color": "#10b981"},
    {"name": "Education", "icon": "📚", "color": "#06b6d4"},
    {"name": "Other", "icon": "📦", "color": "#6b7280"},
]


def get_all_categories(db: Session) -> list[Category]:
    """Fetch all expense categories."""
    return db.query(Category).order_by(Category.name).all()


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    """Fetch a single category by ID."""
    return db.query(Category).filter(Category.id == category_id).first()


def seed_categories(db: Session) -> None:
    """Insert default categories if the table is empty."""
    if db.query(Category).count() == 0:
        for cat_data in DEFAULT_CATEGORIES:
            db.add(Category(**cat_data))
        db.commit()
