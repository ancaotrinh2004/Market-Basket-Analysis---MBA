"""
Recommendation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import (
    RecommendationRequest, 
    RecommendationResponse,
    RecommendedItem
)
from .. import crud

router = APIRouter(prefix="/recommend", tags=["Recommendations"])

@router.post("/", response_model=RecommendationResponse)
def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get product recommendations based on items in cart
    
    **Request Body:**
```json
    {
        "items": ["Milk", "Bread"],
        "top_n": 5,
        "min_confidence": 0.1,
        "min_lift": 1.0
    }
```
    
    **Response:**
    - Recommended items ranked by lift score
    - Includes confidence, lift, support metrics
    - Number of rules that generated each recommendation
    """
    recommendations = crud.get_recommendations(
        db=db,
        items=request.items,
        top_n=request.top_n,
        min_confidence=request.min_confidence,
        min_lift=request.min_lift
    )
    
    # Convert to Pydantic models
    recommended_items = [
        RecommendedItem(**item) for item in recommendations
    ]
    
    return RecommendationResponse(
        request_items=request.items,
        recommended_items=recommended_items,
        total_recommendations=len(recommended_items)
    )

@router.post("/batch")
def get_batch_recommendations(
    requests: list[RecommendationRequest],
    db: Session = Depends(get_db)
):
    """
    Get recommendations for multiple carts (batch processing)
    """
    if len(requests) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 requests per batch"
        )
    
    results = []
    for req in requests:
        recommendations = crud.get_recommendations(
            db=db,
            items=req.items,
            top_n=req.top_n,
            min_confidence=req.min_confidence,
            min_lift=req.min_lift
        )
        
        results.append({
            "request_items": req.items,
            "recommendations": recommendations
        })
    
    return {"total_requests": len(results), "results": results}