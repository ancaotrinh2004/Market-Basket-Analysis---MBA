"""
API Client for FastAPI backend
"""
import requests
import streamlit as st
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            st.error(f"API Error: {response.status_code}")
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {e}")
            st.error(f"Connection Error: Cannot connect to API")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return self._handle_response(response)
        except:
            return {"status": "unhealthy", "database": "disconnected"}
    
    def get_recommendations(
        self,
        items: List[str],
        top_n: int = 5,
        min_confidence: float = 0.1,
        min_lift: float = 1.0
    ) -> Dict[str, Any]:
        """Get product recommendations"""
        payload = {
            "items": items,
            "top_n": top_n,
            "min_confidence": min_confidence,
            "min_lift": min_lift
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/recommend/",
                json=payload,
                timeout=10
            )
            return self._handle_response(response)
        except:
            return {"recommended_items": [], "total_recommendations": 0}
    
    def get_rules(
        self,
        min_confidence: float = 0.0,
        min_lift: float = 0.0,
        min_support: float = 0.0,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get association rules"""
        params = {
            "min_confidence": min_confidence,
            "min_lift": min_lift,
            "min_support": min_support,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/rules/",
                params=params,
                timeout=10
            )
            return self._handle_response(response)
        except:
            return {"total": 0, "rules": []}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rules statistics"""
        try:
            response = requests.get(f"{self.base_url}/rules/stats", timeout=10)
            return self._handle_response(response)
        except:
            return {}
    
    def get_top_items(self, limit: int = 50) -> Dict[str, Any]:
        """Get top items"""
        try:
            response = requests.get(
                f"{self.base_url}/rules/top-items",
                params={"limit": limit},
                timeout=10
            )
            return self._handle_response(response)
        except:
            return {"total": 0, "items": []}
    
    def search_rules(self, item: str, limit: int = 50) -> Dict[str, Any]:
        """Search rules by item"""
        try:
            response = requests.get(
                f"{self.base_url}/rules/search",
                params={"item": item, "limit": limit},
                timeout=10
            )
            return self._handle_response(response)
        except:
            return {"total": 0, "rules": []}