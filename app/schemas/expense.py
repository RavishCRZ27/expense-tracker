from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from app.schemas.category import CategoryResponse


class ExpenseCreate(BaseModel):
    """Schema for creating a new expense."""
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    description: Optional[str] = Field(None, max_length=255)
    date: date
    category_id: int


class ExpenseUpdate(BaseModel):
    """Schema for updating an existing expense."""
    amount: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    description: Optional[str] = Field(None, max_length=255)
    date: Optional[date] = None
    category_id: Optional[int] = None


class ExpenseResponse(BaseModel):
    """Schema for expense data in API responses."""
    id: int
    amount: Decimal
    description: Optional[str]
    date: date
    category_id: int
    category: CategoryResponse
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    """Paginated expense list response."""
    expenses: List[ExpenseResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class DashboardSummary(BaseModel):
    """Dashboard analytics summary."""
    total_spending: Decimal
    average_daily: Decimal
    expense_count: int
    top_category: Optional[str]
    spending_by_category: List[dict]
    daily_trend: List[dict]
    monthly_comparison: List[dict]
