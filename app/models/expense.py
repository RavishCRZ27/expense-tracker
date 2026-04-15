from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Expense(Base):
    """Expense record table - stores individual expense entries with soft delete."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255), nullable=True)
    date = Column(Date, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)

    # Relationships
    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_expenses_user_date", "user_id", "date"),
        Index("ix_expenses_user_category", "user_id", "category_id"),
    )

    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, date='{self.date}')>"
