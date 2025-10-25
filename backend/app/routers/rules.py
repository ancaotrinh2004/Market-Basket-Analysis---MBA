"""
Rules API endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Rule, RulesResponse, StatsResponse
from .. import crud

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.get("/", response_model=RulesResponse)
def get_rules(
    min_confidence: float = Query(0.0, ge=0, le=1, description="Minimum confidence"),
    min_lift: float = Query(0.0, ge=0, description="Minimum lift"),
    min_support: float = Query(0.0, ge=0, le=1, description="Minimum support"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Get association rules with filters
    
    - **min_confidence**: Filter by minimum confidence (0-1)
    - **min_lift**: Filter by minimum lift (>=0)
    - **min_support**: Filter by minimum support (0-1)
    - **limit**: Maximum number of results
    - **offset**: Pagination offset
    """
    rules = crud.get_rules(
        db=db,
        min_confidence=min_confidence,
        min_lift=min_lift,
        min_support=min_support,
        limit=limit,
        offset=offset
    )
    
    total = crud.get_rules_count(
        db=db,
        min_confidence=min_confidence,
        min_lift=min_lift,
        min_support=min_support
    )
    
    return RulesResponse(total=total, rules=rules)

@router.get("/stats", response_model=StatsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about association rules
    """
    stats = crud.get_statistics(db)
    
    if not stats:
        raise HTTPException(status_code=404, detail="No rules found in database")
    
    return StatsResponse(**stats)

@router.get("/top-items")
def get_top_items(
    limit: int = Query(20, ge=1, le=100, description="Number of items"),
    db: Session = Depends(get_db)
):
    """
    Get top items by frequency in rules
    """
    items = crud.get_top_items(db=db, limit=limit)
    return {"total": len(items), "items": items}

@router.get("/search")
def search_rules(
    item: str = Query(..., min_length=1, description="Item name to search"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Search rules containing specific item
    """
    rules = crud.search_rules_by_item(db=db, item_name=item, limit=limit)
    return {"total": len(rules), "rules": rules}