"""
CRUD operations for FP-Growth rules
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def get_rules(
    db: Session,
    min_confidence: float = 0.0,
    min_lift: float = 0.0,
    min_support: float = 0.0,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get rules with filters
    """
    query = text("""
        SELECT 
            antecedent,
            consequent,
            support,
            confidence,
            lift,
            created_at
        FROM fp_growth_rules
        WHERE confidence >= :min_confidence
          AND lift >= :min_lift
          AND support >= :min_support
        ORDER BY lift DESC, confidence DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = db.execute(
        query,
        {
            "min_confidence": min_confidence,
            "min_lift": min_lift,
            "min_support": min_support,
            "limit": limit,
            "offset": offset
        }
    )
    
    return [dict(row._mapping) for row in result]

def get_rules_count(
    db: Session,
    min_confidence: float = 0.0,
    min_lift: float = 0.0,
    min_support: float = 0.0
) -> int:
    """
    Count total rules matching filters
    """
    query = text("""
        SELECT COUNT(*) as count
        FROM fp_growth_rules
        WHERE confidence >= :min_confidence
          AND lift >= :min_lift
          AND support >= :min_support
    """)
    
    result = db.execute(
        query,
        {
            "min_confidence": min_confidence,
            "min_lift": min_lift,
            "min_support": min_support
        }
    ).first()
    
    return result.count if result else 0

def get_recommendations(
    db: Session,
    items: List[str],
    top_n: int = 5,
    min_confidence: float = 0.1,
    min_lift: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Get product recommendations based on cart items
    Uses FP-Growth rules
    """
    if not items:
        return []
    
    # Create placeholders for IN clause
    items_lower = [item.lower() for item in items]
    placeholders = ','.join([f':item{i}' for i in range(len(items))])
    
    query = text(f"""
        WITH matched_rules AS (
            SELECT 
                consequent,
                support,
                confidence,
                lift
            FROM fp_growth_rules
            WHERE LOWER(antecedent) IN ({placeholders})
              AND confidence >= :min_confidence
              AND lift >= :min_lift
              AND LOWER(consequent) NOT IN ({placeholders})
        )
        SELECT 
            consequent AS item_name,
            AVG(lift) AS score,
            AVG(confidence) AS confidence,
            AVG(lift) AS lift,
            AVG(support) AS support,
            COUNT(*) AS matched_rules
        FROM matched_rules
        GROUP BY consequent
        ORDER BY score DESC, confidence DESC
        LIMIT :top_n
    """)
    
    # Prepare parameters
    params = {f'item{i}': item for i, item in enumerate(items_lower)}
    params.update({
        'min_confidence': min_confidence,
        'min_lift': min_lift,
        'top_n': top_n
    })
    
    result = db.execute(query, params)
    return [dict(row._mapping) for row in result]

def get_statistics(db: Session) -> Dict[str, Any]:
    """
    Get statistics about rules
    """
    query = text("""
        SELECT 
            COUNT(*) AS total_rules,
            COUNT(DISTINCT antecedent) + COUNT(DISTINCT consequent) AS total_items,
            AVG(confidence) AS avg_confidence,
            AVG(lift) AS avg_lift,
            AVG(support) AS avg_support,
            MIN(confidence) AS min_confidence,
            MAX(confidence) AS max_confidence,
            MIN(lift) AS min_lift,
            MAX(lift) AS max_lift
        FROM fp_growth_rules
    """)
    
    result = db.execute(query).first()
    
    if not result:
        return {}
    
    return dict(result._mapping)

def get_top_items(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get top items by frequency in rules
    """
    query = text("""
        WITH all_items AS (
            SELECT antecedent AS item_name FROM fp_growth_rules
            UNION ALL
            SELECT consequent FROM fp_growth_rules
        )
        SELECT 
            item_name,
            COUNT(*) AS frequency
        FROM all_items
        GROUP BY item_name
        ORDER BY frequency DESC
        LIMIT :limit
    """)
    
    result = db.execute(query, {"limit": limit})
    return [dict(row._mapping) for row in result]

def search_rules_by_item(
    db: Session,
    item_name: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search rules containing specific item
    """
    query = text("""
        SELECT 
            antecedent,
            consequent,
            support,
            confidence,
            lift
        FROM fp_growth_rules
        WHERE LOWER(antecedent) LIKE LOWER(:pattern)
           OR LOWER(consequent) LIKE LOWER(:pattern)
        ORDER BY lift DESC
        LIMIT :limit
    """)
    
    result = db.execute(
        query,
        {
            "pattern": f"%{item_name}%",
            "limit": limit
        }
    )
    
    return [dict(row._mapping) for row in result]