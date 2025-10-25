"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

# ============= Rules Models =============

class RuleBase(BaseModel):
    antecedent: str
    consequent: str
    support: float
    confidence: float
    lift: float

class Rule(RuleBase):
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RulesResponse(BaseModel):
    total: int
    rules: List[Rule]

# ============= Recommendation Models =============

class RecommendationRequest(BaseModel):
    items: List[str] = Field(..., min_length=1, description="List of items in cart")
    top_n: Optional[int] = Field(5, ge=1, le=50, description="Number of recommendations")
    min_confidence: Optional[float] = Field(0.1, ge=0, le=1)
    min_lift: Optional[float] = Field(1.0, ge=0)
    
    @validator('items')
    def items_not_empty(cls, v):
        if not v or all(not item.strip() for item in v):
            raise ValueError('Items list cannot be empty')
        return [item.strip() for item in v]

class RecommendedItem(BaseModel):
    item_name: str
    score: float = Field(..., description="Recommendation score (avg lift)")
    confidence: float
    lift: float
    support: float
    matched_rules: int = Field(..., description="Number of rules matched")

class RecommendationResponse(BaseModel):
    request_items: List[str]
    recommended_items: List[RecommendedItem]
    total_recommendations: int

# ============= Stats Models =============

class StatsResponse(BaseModel):
    total_rules: int
    total_items: int
    avg_confidence: float
    avg_lift: float
    avg_support: float
    min_confidence: float
    max_confidence: float
    min_lift: float
    max_lift: float

class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime