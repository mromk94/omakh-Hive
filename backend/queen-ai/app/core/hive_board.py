"""
Hive Information Board - Shared Knowledge System

A shared information space where all bees can post and access information.
Reduces Queen's workload by allowing direct bee-to-bee information sharing.

Think of it as:
- Group chat for bees
- Shared memory/knowledge base
- Pheromone trail system
- Information marketplace

Queen retains execution authority but bees can self-coordinate for information.
"""
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import structlog

logger = structlog.get_logger(__name__)


class InformationPost:
    """A single post on the hive board"""
    
    def __init__(
        self,
        author: str,
        category: str,
        title: str,
        content: Dict[str, Any],
        tags: List[str] = None,
        priority: int = 0,
        expires_in_hours: Optional[int] = None,
    ):
        self.id = f"{author}_{category}_{int(datetime.utcnow().timestamp())}"
        self.author = author
        self.category = category
        self.title = title
        self.content = content
        self.tags = tags or []
        self.priority = priority
        self.created_at = datetime.utcnow()
        self.expires_at = (
            datetime.utcnow() + timedelta(hours=expires_in_hours)
            if expires_in_hours
            else None
        )
        self.views = 0
        self.accessed_by: List[str] = []


class HiveInformationBoard:
    """
    Shared information board for all bees
    
    Features:
    - Post information for all bees to see
    - Query information by category/tag/author
    - Subscribe to categories for real-time updates
    - Automatic cleanup of expired posts
    - Access tracking for learning
    - Search functionality
    """
    
    def __init__(self):
        self.posts: Dict[str, InformationPost] = {}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.active = False
        
        # Categories
        self.categories = {
            "market_data": "Price, volume, liquidity data",
            "pool_health": "DEX pool status and health",
            "treasury_status": "Treasury balances and health",
            "security_alerts": "Security warnings and threats",
            "gas_prices": "Current gas price information",
            "staking_info": "Staking APY and rewards",
            "pattern_analysis": "Market patterns and trends",
            "bee_status": "Bee health and availability",
            "decision_outcomes": "Results of Queen's decisions",
            "general": "General information and announcements",
        }
    
    async def initialize(self):
        """Initialize the hive board"""
        self.active = True
        logger.info("🏛️ Hive Information Board initialized")
        logger.info(f"   Available categories: {len(self.categories)}")
    
    async def post(
        self,
        author: str,
        category: str,
        title: str,
        content: Dict[str, Any],
        tags: List[str] = None,
        priority: int = 0,
        expires_in_hours: Optional[int] = 24,
    ) -> str:
        """
        Post information to the board
        
        Args:
            author: Bee posting the information
            category: Information category
            title: Post title
            content: Information payload
            tags: Optional tags for searching
            priority: 0=normal, 1=important, 2=critical
            expires_in_hours: Auto-delete after this many hours (None = never)
            
        Returns:
            Post ID
        """
        if not self.active:
            logger.warning("Hive board not active")
            return None
        
        if category not in self.categories:
            logger.warning(f"Unknown category: {category}")
            category = "general"
        
        # Create post
        post = InformationPost(
            author=author,
            category=category,
            title=title,
            content=content,
            tags=tags,
            priority=priority,
            expires_in_hours=expires_in_hours,
        )
        
        self.posts[post.id] = post
        
        logger.info(
            f"📌 New post on hive board",
            author=author,
            category=category,
            title=title,
            priority=priority
        )
        
        # Notify subscribers
        await self._notify_subscribers(category, post)
        
        return post.id
    
    async def query(
        self,
        category: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        limit: int = 50,
        min_priority: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Query posts from the board
        
        Args:
            category: Filter by category
            author: Filter by author
            tags: Filter by tags (any match)
            since: Only posts after this time
            limit: Maximum posts to return
            min_priority: Minimum priority level
            
        Returns:
            List of matching posts
        """
        # Clean expired posts first
        await self._cleanup_expired()
        
        results = []
        
        for post in self.posts.values():
            # Apply filters
            if category and post.category != category:
                continue
            if author and post.author != author:
                continue
            if tags and not any(tag in post.tags for tag in tags):
                continue
            if since and post.created_at < since:
                continue
            if post.priority < min_priority:
                continue
            
            results.append({
                "id": post.id,
                "author": post.author,
                "category": post.category,
                "title": post.title,
                "content": post.content,
                "tags": post.tags,
                "priority": post.priority,
                "created_at": post.created_at.isoformat(),
                "views": post.views,
            })
        
        # Sort by priority (high to low), then by time (newest first)
        results.sort(key=lambda x: (-x["priority"], -datetime.fromisoformat(x["created_at"]).timestamp()))
        
        return results[:limit]
    
    async def get_post(self, post_id: str, reader: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific post by ID and track access
        
        Args:
            post_id: Post ID to retrieve
            reader: Bee reading the post
            
        Returns:
            Post data or None
        """
        post = self.posts.get(post_id)
        if not post:
            return None
        
        # Track access
        post.views += 1
        if reader not in post.accessed_by:
            post.accessed_by.append(reader)
        
        return {
            "id": post.id,
            "author": post.author,
            "category": post.category,
            "title": post.title,
            "content": post.content,
            "tags": post.tags,
            "priority": post.priority,
            "created_at": post.created_at.isoformat(),
            "views": post.views,
            "accessed_by": post.accessed_by,
        }
    
    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search posts by keyword
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Matching posts
        """
        query_lower = query.lower()
        results = []
        
        for post in self.posts.values():
            # Search in title, tags, and category
            if (
                query_lower in post.title.lower() or
                query_lower in post.category.lower() or
                any(query_lower in tag.lower() for tag in post.tags)
            ):
                results.append({
                    "id": post.id,
                    "author": post.author,
                    "category": post.category,
                    "title": post.title,
                    "content": post.content,
                    "created_at": post.created_at.isoformat(),
                    "relevance": self._calculate_relevance(post, query_lower),
                })
        
        # Sort by relevance
        results.sort(key=lambda x: -x["relevance"])
        
        return results[:limit]
    
    async def subscribe(
        self,
        category: str,
        callback: Callable,
    ):
        """
        Subscribe to a category for real-time updates
        
        Args:
            category: Category to subscribe to
            callback: Function to call when new posts arrive
        """
        self.subscribers[category].append(callback)
        logger.info(f"New subscriber to {category}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get board statistics"""
        total_posts = len(self.posts)
        
        # Posts by category
        by_category = defaultdict(int)
        for post in self.posts.values():
            by_category[post.category] += 1
        
        # Posts by author
        by_author = defaultdict(int)
        for post in self.posts.values():
            by_author[post.author] += 1
        
        # Most viewed posts
        sorted_by_views = sorted(
            self.posts.values(),
            key=lambda p: p.views,
            reverse=True
        )[:5]
        
        most_viewed = [
            {
                "title": p.title,
                "author": p.author,
                "views": p.views,
            }
            for p in sorted_by_views
        ]
        
        return {
            "total_posts": total_posts,
            "active_categories": len(by_category),
            "posts_by_category": dict(by_category),
            "posts_by_author": dict(by_author),
            "total_subscribers": sum(len(subs) for subs in self.subscribers.values()),
            "most_viewed": most_viewed,
        }
    
    async def _cleanup_expired(self):
        """Remove expired posts"""
        now = datetime.utcnow()
        expired = [
            post_id
            for post_id, post in self.posts.items()
            if post.expires_at and post.expires_at < now
        ]
        
        for post_id in expired:
            del self.posts[post_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired posts")
    
    async def _notify_subscribers(self, category: str, post: InformationPost):
        """Notify subscribers of new post"""
        if category in self.subscribers:
            for callback in self.subscribers[category]:
                try:
                    await callback(post)
                except Exception as e:
                    logger.error(f"Error notifying subscriber: {e}")
    
    def _calculate_relevance(self, post: InformationPost, query: str) -> float:
        """Calculate search relevance score"""
        score = 0.0
        
        # Title match (highest weight)
        if query in post.title.lower():
            score += 10.0
        
        # Category match
        if query in post.category.lower():
            score += 5.0
        
        # Tag match
        for tag in post.tags:
            if query in tag.lower():
                score += 3.0
        
        # Boost for priority
        score += post.priority * 2.0
        
        # Boost for recency (newer = higher score)
        age_hours = (datetime.utcnow() - post.created_at).total_seconds() / 3600
        score += max(0, 10 - age_hours)  # Up to 10 points for very recent
        
        return score
    
    async def shutdown(self):
        """Shutdown the board"""
        self.active = False
        logger.info("Hive Information Board shutdown")


# Example usage for bees:
"""
# MathsBee posts pool analysis
await hive_board.post(
    author="maths",
    category="pool_health",
    title="Uniswap OMK/ETH pool needs rebalancing",
    content={
        "pool_address": "0x...",
        "current_ratio": 1.15,
        "target_ratio": 1.0,
        "deviation": 15,
        "recommended_action": "add_liquidity",
        "amount_needed": 2_000_000 * 10**18,
    },
    tags=["uniswap", "liquidity", "urgent"],
    priority=1,
    expires_in_hours=6,
)

# PurchaseBee queries current gas prices
gas_posts = await hive_board.query(
    category="gas_prices",
    limit=1,  # Get most recent
)

# SecurityBee subscribes to security alerts
async def on_security_alert(post):
    logger.critical(f"SECURITY ALERT: {post.title}")
    
await hive_board.subscribe("security_alerts", on_security_alert)

# Any bee searches for liquidity info
results = await hive_board.search("liquidity uniswap")
"""
