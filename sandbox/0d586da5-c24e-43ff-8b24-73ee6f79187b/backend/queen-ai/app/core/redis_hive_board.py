"""
Redis-backed Hive Information Board - Persistent Shared Knowledge

Replaces in-memory HiveInformationBoard with Redis for production.
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class RedisHiveBoard:
    """
    Redis-backed shared knowledge board for bees
    
    Redis Data Structures:
    - post:{post_id} - Hash (post data)
    - posts:by_category:{category} - Sorted Set (by timestamp)
    - posts:by_author:{author} - Sorted Set (by timestamp)
    - posts:all - Sorted Set (all posts by timestamp)
    - post_id:counter - String (auto-increment counter)
    """
    
    CATEGORIES = [
        "pool_health", "treasury", "governance", "staking_info",
        "security_alert", "market_analysis", "transaction",
        "proposal", "recommendation", "general"
    ]
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.initialized = False
        self.default_ttl = 86400 * 7  # 7 days
        
        if not REDIS_AVAILABLE:
            logger.warning("⚠️  redis package not installed")
    
    async def initialize(self):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            return
        
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            await self.redis.ping()
            self.initialized = True
            
            logger.info("✅ Redis Hive Board initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hive Board: {str(e)}")
            self.initialized = False
    
    async def post(
        self,
        author: str,
        category: str,
        title: str,
        content: Dict[str, Any],
        tags: Optional[List[str]] = None,
        ttl: Optional[int] = None
    ) -> Optional[int]:
        """
        Create a post on the hive board
        
        Returns:
            Post ID if successful
        """
        if not self.initialized:
            return None
        
        try:
            # Validate category
            if category not in self.CATEGORIES:
                logger.warning(f"Invalid category: {category}")
                return None
            
            # Generate post ID
            post_id = await self.redis.incr("post_id:counter")
            
            # Create post data
            timestamp = datetime.utcnow()
            post = {
                "post_id": post_id,
                "author": author,
                "category": category,
                "title": title,
                "content": json.dumps(content),
                "tags": json.dumps(tags or []),
                "created_at": timestamp.isoformat(),
                "expires_at": (timestamp + timedelta(seconds=ttl or self.default_ttl)).isoformat()
            }
            
            # Store post as hash
            post_key = f"post:{post_id}"
            await self.redis.hset(post_key, mapping=post)
            
            # Set TTL
            await self.redis.expire(post_key, ttl or self.default_ttl)
            
            # Add to sorted sets for indexing
            score = int(timestamp.timestamp() * 1000)
            
            await self.redis.zadd(f"posts:by_category:{category}", {str(post_id): score})
            await self.redis.zadd(f"posts:by_author:{author}", {str(post_id): score})
            await self.redis.zadd("posts:all", {str(post_id): score})
            
            logger.info(
                f"Post created",
                post_id=post_id,
                author=author,
                category=category
            )
            
            return post_id
            
        except Exception as e:
            logger.error(f"Failed to create post: {str(e)}")
            return None
    
    async def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific post"""
        if not self.initialized:
            return None
        
        try:
            post_data = await self.redis.hgetall(f"post:{post_id}")
            
            if not post_data:
                return None
            
            # Parse JSON fields
            post_data["content"] = json.loads(post_data["content"])
            post_data["tags"] = json.loads(post_data["tags"])
            post_data["post_id"] = int(post_data["post_id"])
            
            return post_data
            
        except Exception as e:
            logger.error(f"Failed to get post: {str(e)}")
            return None
    
    async def query(
        self,
        category: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Query posts by category or author
        
        Returns most recent posts
        """
        if not self.initialized:
            return []
        
        try:
            # Determine which index to use
            if category:
                index_key = f"posts:by_category:{category}"
            elif author:
                index_key = f"posts:by_author:{author}"
            else:
                index_key = "posts:all"
            
            # Get post IDs (most recent first)
            post_ids = await self.redis.zrevrange(index_key, 0, limit - 1)
            
            # Fetch posts
            posts = []
            for post_id_str in post_ids:
                post = await self.get_post(int(post_id_str))
                if post:
                    posts.append(post)
            
            return posts
            
        except Exception as e:
            logger.error(f"Failed to query posts: {str(e)}")
            return []
    
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search posts by title or tags
        
        Simple implementation - gets posts and filters in memory.
        For production, consider using Redis Search module.
        """
        if not self.initialized:
            return []
        
        try:
            # Get posts from category or all
            posts = await self.query(category=category, limit=limit * 2)
            
            # Filter by query string (case-insensitive)
            query_lower = query.lower()
            matching_posts = []
            
            for post in posts:
                # Check title
                if query_lower in post["title"].lower():
                    matching_posts.append(post)
                    continue
                
                # Check tags
                if any(query_lower in tag.lower() for tag in post["tags"]):
                    matching_posts.append(post)
                    continue
            
            return matching_posts[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search posts: {str(e)}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get board statistics"""
        if not self.initialized:
            return {}
        
        try:
            # Total posts
            total_posts = await self.redis.zcard("posts:all")
            
            # Posts by category
            category_counts = {}
            for category in self.CATEGORIES:
                count = await self.redis.zcard(f"posts:by_category:{category}")
                if count > 0:
                    category_counts[category] = count
            
            # Recent activity (last hour)
            one_hour_ago = int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)
            recent_posts = await self.redis.zcount("posts:all", one_hour_ago, "+inf")
            
            return {
                "total_posts": total_posts,
                "posts_by_category": category_counts,
                "posts_last_hour": recent_posts,
                "categories": self.CATEGORIES
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {}
    
    async def delete_post(self, post_id: int) -> bool:
        """Delete a post (admin function)"""
        if not self.initialized:
            return False
        
        try:
            # Get post to find category/author
            post = await self.get_post(post_id)
            if not post:
                return False
            
            # Remove from all indexes
            await self.redis.zrem(f"posts:by_category:{post['category']}", str(post_id))
            await self.redis.zrem(f"posts:by_author:{post['author']}", str(post_id))
            await self.redis.zrem("posts:all", str(post_id))
            
            # Delete post data
            await self.redis.delete(f"post:{post_id}")
            
            logger.info(f"Post deleted: {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete post: {str(e)}")
            return False
    
    async def cleanup_expired(self) -> int:
        """
        Cleanup expired posts from indexes
        
        Redis auto-deletes with TTL, but need to clean indexes
        """
        if not self.initialized:
            return 0
        
        try:
            cleaned = 0
            
            # Get all post IDs from index
            all_post_ids = await self.redis.zrange("posts:all", 0, -1)
            
            for post_id_str in all_post_ids:
                # Check if post still exists
                exists = await self.redis.exists(f"post:{post_id_str}")
                
                if not exists:
                    # Remove from all indexes
                    await self.redis.zrem("posts:all", post_id_str)
                    
                    # Remove from category indexes (check all categories)
                    for category in self.CATEGORIES:
                        await self.redis.zrem(f"posts:by_category:{category}", post_id_str)
                    
                    cleaned += 1
            
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired posts from indexes")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup: {str(e)}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis health"""
        if not self.initialized:
            return {"healthy": False, "error": "Not initialized"}
        
        try:
            await self.redis.ping()
            total_posts = await self.redis.zcard("posts:all")
            
            return {
                "healthy": True,
                "total_posts": total_posts
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def shutdown(self):
        """Cleanup"""
        if self.redis:
            await self.redis.close()
        
        logger.info("Redis Hive Board shutdown")
