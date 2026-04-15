from pydantic import BaseModel
from typing import Optional


class CategoryResponse(BaseModel):
    """Schema for category data in API responses."""
    id: int
    name: str
    icon: str
    color: str

    class Config:
        from_attributes = True
