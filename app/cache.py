"""
Caching layer for authorization service.
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import OrderedDict
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class CacheEntry:
    """Cache entry with expiration."""
    
    def __init__(self, value: Any, ttl: int):
        """Initialize cache entry.
        
        Args:
            value: Cached value
            ttl: Time to live in seconds
        """
        self.value = value
        self.expiry = datetime.utcnow() + timedelta(seconds=ttl)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.expiry


class LRUCache:
    """Thread-safe LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        """Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items in cache
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key not in self.cache:
                self._misses += 1
                return None
            
            entry = self.cache[key]
            
            if entry.is_expired():
                del self.cache[key]
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self._hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl
            
            entry = CacheEntry(value, ttl)
            
            if key in self.cache:
                # Update existing entry
                self.cache[key] = entry
                self.cache.move_to_end(key)
            else:
                # Add new entry
                self.cache[key] = entry
                
                # Evict LRU item if cache is full
                if len(self.cache) > self.max_size:
                    self.cache.popitem(last=False)
    
    def delete(self, key: str):
        """Delete value from cache.
        
        Args:
            key: Cache key
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self._hits = 0
            self._misses = 0
    
    def clear_pattern(self, pattern: str):
        """Clear cache entries matching pattern.
        
        Args:
            pattern: Pattern to match (supports * wildcard)
        """
        with self.lock:
            keys_to_delete = []
            
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                keys_to_delete = [k for k in self.cache.keys() if k.startswith(prefix)]
            elif pattern.startswith("*"):
                suffix = pattern[1:]
                keys_to_delete = [k for k in self.cache.keys() if k.endswith(suffix)]
            elif "*" in pattern:
                parts = pattern.split("*")
                keys_to_delete = [k for k in self.cache.keys() 
                                if k.startswith(parts[0]) and k.endswith(parts[1])]
            else:
                # Exact match
                if pattern in self.cache:
                    keys_to_delete = [pattern]
            
            for key in keys_to_delete:
                del self.cache[key]
            
            logger.info(f"Cleared {len(keys_to_delete)} cache entries matching pattern: {pattern}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%"
            }


class PolicyCache:
    """Cache for policy data."""
    
    def __init__(self, policy_ttl: int = 300, role_ttl: int = 120, 
                 decision_ttl: int = 30, max_size: int = 10000):
        """Initialize policy cache.
        
        Args:
            policy_ttl: Policy cache TTL in seconds
            role_ttl: Role cache TTL in seconds
            decision_ttl: Decision cache TTL in seconds
            max_size: Maximum cache size
        """
        self.policy_cache = LRUCache(max_size=max_size, default_ttl=policy_ttl)
        self.role_cache = LRUCache(max_size=max_size, default_ttl=role_ttl)
        self.decision_cache = LRUCache(max_size=max_size, default_ttl=decision_ttl)
    
    # Policy cache methods
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy from cache."""
        return self.policy_cache.get(f"policy:{policy_id}")
    
    def set_policy(self, policy_id: str, policy: Dict[str, Any]):
        """Set policy in cache."""
        self.policy_cache.set(f"policy:{policy_id}", policy)
    
    def delete_policy(self, policy_id: str):
        """Delete policy from cache."""
        self.policy_cache.delete(f"policy:{policy_id}")
    
    def get_tenant_policies(self, tenant_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get tenant policies from cache."""
        return self.policy_cache.get(f"tenant_policies:{tenant_id}")
    
    def set_tenant_policies(self, tenant_id: str, policies: List[Dict[str, Any]]):
        """Set tenant policies in cache."""
        self.policy_cache.set(f"tenant_policies:{tenant_id}", policies)
    
    # Role cache methods
    def get_user_roles(self, user_id: str, tenant_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get user roles from cache."""
        return self.role_cache.get(f"user_roles:{user_id}:{tenant_id}")
    
    def set_user_roles(self, user_id: str, tenant_id: str, roles: List[Dict[str, Any]]):
        """Set user roles in cache."""
        self.role_cache.set(f"user_roles:{user_id}:{tenant_id}", roles)
    
    def delete_user_roles(self, user_id: str, tenant_id: str):
        """Delete user roles from cache."""
        self.role_cache.delete(f"user_roles:{user_id}:{tenant_id}")
    
    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Get role from cache."""
        return self.role_cache.get(f"role:{role_id}")
    
    def set_role(self, role_id: str, role: Dict[str, Any]):
        """Set role in cache."""
        self.role_cache.set(f"role:{role_id}", role)
    
    def delete_role(self, role_id: str):
        """Delete role from cache."""
        self.role_cache.delete(f"role:{role_id}")
    
    # Decision cache methods
    def get_decision(self, decision_key: str) -> Optional[Dict[str, Any]]:
        """Get decision from cache."""
        return self.decision_cache.get(f"decision:{decision_key}")
    
    def set_decision(self, decision_key: str, decision: Dict[str, Any]):
        """Set decision in cache."""
        self.decision_cache.set(f"decision:{decision_key}", decision)
    
    # Clear methods
    def clear_all(self):
        """Clear all caches."""
        self.policy_cache.clear()
        self.role_cache.clear()
        self.decision_cache.clear()
        logger.info("Cleared all caches")
    
    def clear_tenant(self, tenant_id: str):
        """Clear all cache entries for a tenant."""
        self.policy_cache.clear_pattern(f"*:{tenant_id}*")
        self.role_cache.clear_pattern(f"*:{tenant_id}*")
        self.decision_cache.clear_pattern(f"*:{tenant_id}*")
        logger.info(f"Cleared cache for tenant: {tenant_id}")
    
    def clear_user(self, user_id: str):
        """Clear all cache entries for a user."""
        self.role_cache.clear_pattern(f"user_roles:{user_id}:*")
        self.decision_cache.clear_pattern(f"decision:*:{user_id}:*")
        logger.info(f"Cleared cache for user: {user_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "policy_cache": self.policy_cache.get_stats(),
            "role_cache": self.role_cache.get_stats(),
            "decision_cache": self.decision_cache.get_stats()
        }


# Global cache instance
_cache: Optional[PolicyCache] = None


def get_cache() -> PolicyCache:
    """Get global cache instance."""
    global _cache
    if _cache is None:
        from app.config import get_config
        config = get_config()
        _cache = PolicyCache(
            policy_ttl=config.cache.policy_ttl,
            role_ttl=config.cache.role_ttl,
            decision_ttl=config.cache.decision_ttl,
            max_size=config.cache.max_size
        )
    return _cache
