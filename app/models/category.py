from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    """Expense category table - predefined categories for classifying expenses."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    icon = Column(String(10), nullable=False, default="📦")
    color = Column(String(7), nullable=False, default="#6366f1")

    # Relationships
    expenses = relationship("Expense", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
