"""
Database Query Tool for Queen AI

Allows Queen to query the database with natural language
and answer questions about users, system state, etc.
"""

import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.db.models import User, GovernanceProposal, Vote, PrivateSalePurchase

logger = structlog.get_logger(__name__)


class DatabaseQueryTool:
    """
    Powerful database query tool for Queen AI
    
    Allows natural language queries like:
    - "How many female users in Tokyo with $500-$1950 in wallet?"
    - "Show me top 10 most active users this week"
    - "What's the average wallet balance by region?"
    """
    
    def __init__(self):
        self.db: Optional[Session] = None
    
    def _get_db(self) -> Session:
        """Get database session"""
        if self.db is None:
            self.db = SessionLocal()
        return self.db
    
    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None
    
    # ==================== USER QUERIES ====================
    
    async def query_users(
        self,
        gender: Optional[str] = None,
        region: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        wallet_min: Optional[float] = None,
        wallet_max: Optional[float] = None,
        is_active: Optional[bool] = None,
        kyc_verified: Optional[bool] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        created_after: Optional[datetime] = None,
        last_active_after: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query users with complex filters
        
        Example:
            result = await query_users(
                gender="female",
                region="Tokyo",
                wallet_min=500,
                wallet_max=1950,
                is_active=True
            )
        
        Returns:
            {
                "count": 42,
                "users": [...],
                "summary": {...}
            }
        """
        try:
            db = self._get_db()
            query = db.query(User)
            
            # Apply filters
            filters = []
            
            if gender:
                filters.append(User.gender == gender.lower())
            
            if region:
                filters.append(User.region.ilike(f"%{region}%"))
            
            if country:
                filters.append(User.country.ilike(f"%{country}%"))
            
            if city:
                filters.append(User.city.ilike(f"%{city}%"))
            
            if wallet_min is not None:
                filters.append(User.wallet_balance_usd >= wallet_min)
            
            if wallet_max is not None:
                filters.append(User.wallet_balance_usd <= wallet_max)
            
            if is_active is not None:
                filters.append(User.is_active == is_active)
            
            if kyc_verified is not None:
                filters.append(User.kyc_verified == kyc_verified)
            
            if min_age:
                filters.append(User.age >= min_age)
            
            if max_age:
                filters.append(User.age <= max_age)
            
            if created_after:
                filters.append(User.created_at >= created_after)
            
            if last_active_after:
                filters.append(User.last_active >= last_active_after)
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Get results
            total_count = query.count()
            users = query.limit(limit).all()
            
            # Convert to dicts
            user_list = []
            for user in users:
                user_list.append({
                    "id": user.id,
                    "email": user.email,
                    "wallet_address": user.wallet_address,
                    "gender": user.gender,
                    "age": user.age,
                    "country": user.country,
                    "region": user.region,
                    "city": user.city,
                    "wallet_balance_usd": float(user.wallet_balance_usd) if user.wallet_balance_usd else 0,
                    "is_active": user.is_active,
                    "kyc_verified": user.kyc_verified,
                    "last_active": user.last_active.isoformat() if user.last_active else None,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                })
            
            # Calculate summary statistics
            summary = await self._calculate_user_summary(query)
            
            logger.info(
                "User query executed",
                filters=len(filters),
                results=total_count
            )
            
            return {
                "success": True,
                "count": total_count,
                "returned": len(user_list),
                "users": user_list,
                "summary": summary,
                "query_time": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"User query failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "count": 0,
                "users": []
            }
    
    async def _calculate_user_summary(self, query) -> Dict[str, Any]:
        """Calculate summary statistics for user query"""
        try:
            db = self._get_db()
            
            # Use the filtered query
            total_balance = db.query(func.sum(User.wallet_balance_usd)).filter(
                User.id.in_([u.id for u in query.all()])
            ).scalar() or 0
            
            avg_balance = db.query(func.avg(User.wallet_balance_usd)).filter(
                User.id.in_([u.id for u in query.all()])
            ).scalar() or 0
            
            return {
                "total_wallet_balance": float(total_balance),
                "average_wallet_balance": float(avg_balance),
                "active_users": query.filter(User.is_active == True).count(),
                "kyc_verified_users": query.filter(User.kyc_verified == True).count()
            }
        except Exception as e:
            logger.error(f"Summary calculation failed: {str(e)}")
            return {}
    
    async def get_top_users_by_activity(self, limit: int = 10, days: int = 7) -> Dict[str, Any]:
        """Get most active users in the last N days"""
        try:
            db = self._get_db()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            users = db.query(User).filter(
                User.last_active >= cutoff_date
            ).order_by(User.activity_score.desc()).limit(limit).all()
            
            user_list = []
            for user in users:
                user_list.append({
                    "id": user.id,
                    "email": user.email,
                    "activity_score": user.activity_score,
                    "last_active": user.last_active.isoformat() if user.last_active else None,
                    "wallet_balance_usd": float(user.wallet_balance_usd) if user.wallet_balance_usd else 0
                })
            
            return {
                "success": True,
                "top_users": user_list,
                "period_days": days
            }
        
        except Exception as e:
            logger.error(f"Top users query failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get overall user statistics"""
        try:
            db = self._get_db()
            
            stats = {
                "total_users": db.query(User).count(),
                "active_users": db.query(User).filter(User.is_active == True).count(),
                "kyc_verified": db.query(User).filter(User.kyc_verified == True).count(),
                "total_wallet_balance": float(db.query(func.sum(User.wallet_balance_usd)).scalar() or 0),
                "average_wallet_balance": float(db.query(func.avg(User.wallet_balance_usd)).scalar() or 0),
                "users_by_region": await self._get_users_by_region(),
                "users_by_gender": await self._get_users_by_gender()
            }
            
            return {
                "success": True,
                "statistics": stats
            }
        
        except Exception as e:
            logger.error(f"Statistics query failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_users_by_region(self) -> Dict[str, int]:
        """Get user count by region"""
        try:
            db = self._get_db()
            results = db.query(User.region, func.count(User.id)).group_by(User.region).all()
            return {region: count for region, count in results if region}
        except:
            return {}
    
    async def _get_users_by_gender(self) -> Dict[str, int]:
        """Get user count by gender"""
        try:
            db = self._get_db()
            results = db.query(User.gender, func.count(User.id)).group_by(User.gender).all()
            return {gender: count for gender, count in results if gender}
        except:
            return {}
    
    # ==================== GOVERNANCE QUERIES ====================
    
    async def get_active_proposals(self) -> Dict[str, Any]:
        """Get all active governance proposals"""
        try:
            db = self._get_db()
            proposals = db.query(GovernanceProposal).filter(
                GovernanceProposal.status == "ACTIVE"
            ).all()
            
            proposal_list = []
            for prop in proposals:
                proposal_list.append({
                    "id": prop.id,
                    "proposal_id": prop.proposal_id,
                    "title": prop.title,
                    "proposer": prop.proposer,
                    "votes_for": float(prop.votes_for) if prop.votes_for else 0,
                    "votes_against": float(prop.votes_against) if prop.votes_against else 0,
                    "votes_abstain": float(prop.votes_abstain) if prop.votes_abstain else 0,
                    "created_at": prop.created_at.isoformat() if prop.created_at else None
                })
            
            return {
                "success": True,
                "count": len(proposal_list),
                "proposals": proposal_list
            }
        
        except Exception as e:
            logger.error(f"Proposals query failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== NATURAL LANGUAGE INTERFACE ====================
    
    async def natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Convert natural language query to SQL and execute
        
        Examples:
        - "How many female users in Tokyo with $500-$1950 in wallet?"
        - "Show me top 10 most active users"
        - "What's the average wallet balance by region?"
        """
        try:
            # Parse query and extract parameters
            params = self._parse_natural_language(query)
            
            # Route to appropriate query method
            if "users" in query.lower():
                if "top" in query.lower() and "active" in query.lower():
                    limit = self._extract_number(query) or 10
                    return await self.get_top_users_by_activity(limit=limit)
                elif "statistics" in query.lower() or "stats" in query.lower():
                    return await self.get_user_statistics()
                else:
                    return await self.query_users(**params)
            
            elif "proposal" in query.lower():
                return await self.get_active_proposals()
            
            else:
                return {
                    "success": False,
                    "error": "Could not understand query. Try being more specific about users or proposals."
                }
        
        except Exception as e:
            logger.error(f"Natural language query failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_natural_language(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into parameters"""
        params = {}
        query_lower = query.lower()
        
        # Gender
        if "female" in query_lower:
            params["gender"] = "female"
        elif "male" in query_lower and "female" not in query_lower:
            params["gender"] = "male"
        
        # Location
        locations = ["tokyo", "new york", "london", "paris", "singapore", "dubai", "hong kong"]
        for loc in locations:
            if loc in query_lower:
                params["region"] = loc.title()
                break
        
        # Wallet balance
        if "$" in query or "usd" in query_lower:
            numbers = self._extract_numbers(query)
            if len(numbers) >= 2:
                params["wallet_min"] = min(numbers)
                params["wallet_max"] = max(numbers)
            elif len(numbers) == 1:
                if "above" in query_lower or "more than" in query_lower:
                    params["wallet_min"] = numbers[0]
                elif "below" in query_lower or "less than" in query_lower:
                    params["wallet_max"] = numbers[0]
        
        # Active status
        if "active" in query_lower:
            params["is_active"] = True
        
        # KYC
        if "kyc" in query_lower or "verified" in query_lower:
            params["kyc_verified"] = True
        
        return params
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        import re
        # Remove commas from numbers
        text = text.replace(",", "")
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(n) for n in numbers]
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract first number from text"""
        numbers = self._extract_numbers(text)
        return int(numbers[0]) if numbers else None
