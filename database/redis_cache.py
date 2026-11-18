"""
Redis Cache Manager
Handles caching for OTP, sessions, and LLM responses
"""

import os
import json
import redis
from typing import Optional, Any, Dict
from dotenv import load_dotenv
from datetime import datetime, timedelta, date

load_dotenv()

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def parse_datetime_strings(obj):
    """Recursively parse ISO format datetime strings back to datetime objects"""
    if isinstance(obj, dict):
        return {key: parse_datetime_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [parse_datetime_strings(item) for item in obj]
    elif isinstance(obj, str):
        # Try to parse ISO format datetime strings
        try:
            # Check if string looks like ISO datetime
            if 'T' in obj and len(obj) > 18:
                return datetime.fromisoformat(obj.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pass
    return obj

class RedisCache:
    """Singleton Redis cache manager"""
    
    _instance = None
    _redis_client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._redis_client is None:
            self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self._redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_DB", "0")),
                password=os.getenv("REDIS_PASSWORD", None),
                decode_responses=True,  # Auto-decode bytes to strings
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self._redis_client.ping()
            print("✅ Redis cache initialized")
        except redis.ConnectionError as e:
            print(f"⚠️ Redis not available: {e}")
            print("   Falling back to in-memory cache")
            self._redis_client = None
        except Exception as e:
            print(f"❌ Redis initialization error: {e}")
            self._redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self._redis_client is not None
    
    # ========================================================================
    # BASIC CACHE OPERATIONS
    # ========================================================================
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set cache value with optional TTL
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON-serialized if dict/list)
            ttl: Time to live in seconds (None = no expiry)
        """
        if not self.is_available():
            return False
        
        try:
            # Serialize complex types with datetime support
            if isinstance(value, (dict, list)):
                value = json.dumps(value, cls=DateTimeEncoder)
            
            if ttl:
                return self._redis_client.setex(key, ttl, value)
            else:
                return self._redis_client.set(key, value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get cache value"""
        if not self.is_available():
            return default
        
        try:
            value = self._redis_client.get(key)
            if value is None:
                return default
            
            # Try to deserialize JSON and parse datetime strings
            try:
                parsed = json.loads(value)
                # Parse datetime strings back to datetime objects
                return parse_datetime_strings(parsed)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            print(f"Redis get error: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """Delete cache key"""
        if not self.is_available():
            return False
        
        try:
            return self._redis_client.delete(key) > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.is_available():
            return False
        
        try:
            return self._redis_client.exists(key) > 0
        except Exception as e:
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        if not self.is_available():
            return -1
        
        try:
            return self._redis_client.ttl(key)
        except Exception as e:
            return -1
    
    # ========================================================================
    # OTP CACHE OPERATIONS
    # ========================================================================
    
    def set_otp(self, phone: str, otp_code: str, ttl: int = 300) -> bool:
        """
        Cache OTP code for phone number
        
        Args:
            phone: Phone number
            otp_code: OTP code
            ttl: Time to live in seconds (default 5 minutes)
        """
        key = f"otp:{phone}"
        data = {
            "code": otp_code,
            "attempts": 0,
            "max_attempts": 3
        }
        return self.set(key, data, ttl)
    
    def verify_otp(self, phone: str, otp_code: str) -> bool:
        """
        Verify OTP code and increment attempts
        
        Returns:
            True if OTP is valid, False otherwise
        """
        key = f"otp:{phone}"
        data = self.get(key)
        
        if not data:
            return False
        
        # Check if max attempts exceeded
        if data.get("attempts", 0) >= data.get("max_attempts", 3):
            self.delete(key)
            return False
        
        # Check if OTP matches
        if data.get("code") == otp_code:
            self.delete(key)  # OTP used, delete it
            return True
        else:
            # Increment attempts
            data["attempts"] += 1
            ttl = self.get_ttl(key)
            if ttl > 0:
                self.set(key, data, ttl)
            return False
    
    def get_otp_attempts(self, phone: str) -> int:
        """Get number of OTP verification attempts"""
        key = f"otp:{phone}"
        data = self.get(key)
        return data.get("attempts", 0) if data else 0
    
    # ========================================================================
    # SESSION CACHE OPERATIONS
    # ========================================================================
    
    def set_session(self, session_id: str, session_data: Dict, ttl: int = 3600) -> bool:
        """
        Cache session data
        
        Args:
            session_id: Unique session identifier
            session_data: Session data dictionary
            ttl: Time to live in seconds (default 1 hour)
        """
        key = f"session:{session_id}"
        return self.set(key, session_data, ttl)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        key = f"session:{session_id}"
        return self.get(key)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        key = f"session:{session_id}"
        return self.delete(key)
    
    def refresh_session(self, session_id: str, ttl: int = 3600) -> bool:
        """Extend session TTL"""
        key = f"session:{session_id}"
        if not self.exists(key):
            return False
        
        try:
            return self._redis_client.expire(key, ttl)
        except:
            return False
    
    # ========================================================================
    # LLM RESPONSE CACHE OPERATIONS
    # ========================================================================
    
    def cache_llm_response(self, prompt: str, response: str, ttl: int = 1800) -> bool:
        """
        Cache LLM response for prompt
        
        Args:
            prompt: Input prompt
            response: LLM response
            ttl: Time to live in seconds (default 30 minutes)
        """
        # Create hash of prompt for key
        import hashlib
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        key = f"llm:{prompt_hash}"
        return self.set(key, response, ttl)
    
    def get_cached_llm_response(self, prompt: str) -> Optional[str]:
        """Get cached LLM response for prompt"""
        import hashlib
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        key = f"llm:{prompt_hash}"
        return self.get(key)
    
    # ========================================================================
    # WORKFLOW STATE CACHE
    # ========================================================================
    
    def cache_workflow_state(self, patient_id: str, state: Dict, ttl: int = 7200) -> bool:
        """
        Cache workflow state for quick access
        
        Args:
            patient_id: Patient ID
            state: Workflow state dictionary
            ttl: Time to live in seconds (default 2 hours)
        """
        key = f"workflow:{patient_id}"
        return self.set(key, state, ttl)
    
    def get_cached_workflow_state(self, patient_id: str) -> Optional[Dict]:
        """Get cached workflow state"""
        key = f"workflow:{patient_id}"
        return self.get(key)
    
    def invalidate_workflow_cache(self, patient_id: str) -> bool:
        """Invalidate workflow cache"""
        key = f"workflow:{patient_id}"
        return self.delete(key)
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    def check_rate_limit(self, identifier: str, max_requests: int = 10, 
                        window: int = 60) -> bool:
        """
        Check if rate limit exceeded
        
        Args:
            identifier: Unique identifier (email, IP, etc.)
            max_requests: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            True if under limit, False if exceeded
        """
        if not self.is_available():
            return True  # Allow if Redis unavailable
        
        key = f"ratelimit:{identifier}"
        
        try:
            count = self._redis_client.incr(key)
            
            if count == 1:
                # First request, set expiry
                self._redis_client.expire(key, window)
            
            return count <= max_requests
        except Exception as e:
            print(f"Rate limit check error: {e}")
            return True  # Allow on error
    
    def get_rate_limit_remaining(self, identifier: str, max_requests: int = 10) -> int:
        """Get remaining requests in current window"""
        key = f"ratelimit:{identifier}"
        count = self.get(key) or 0
        try:
            count = int(count)
        except:
            count = 0
        return max(0, max_requests - count)
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def flush_all(self) -> bool:
        """Flush all cache (USE WITH CAUTION)"""
        if not self.is_available():
            return False
        
        try:
            self._redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Flush error: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get Redis statistics"""
        if not self.is_available():
            return {"status": "unavailable"}
        
        try:
            info = self._redis_client.info()
            return {
                "status": "connected",
                "used_memory_human": info.get("used_memory_human"),
                "total_keys": self._redis_client.dbsize(),
                "connected_clients": info.get("connected_clients"),
                "uptime_in_seconds": info.get("uptime_in_seconds")
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ============================================================================
# IN-MEMORY FALLBACK CACHE
# ============================================================================

class InMemoryCache:
    """Fallback in-memory cache when Redis is unavailable"""
    
    def __init__(self):
        self._cache = {}
        self._ttl = {}
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cache value"""
        import time
        self._cache[key] = value
        if ttl:
            self._ttl[key] = time.time() + ttl
        return True
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get cache value"""
        import time
        
        # Check if expired
        if key in self._ttl and time.time() > self._ttl[key]:
            self.delete(key)
            return default
        
        return self._cache.get(key, default)
    
    def delete(self, key: str) -> bool:
        """Delete cache key"""
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]
        return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return key in self._cache


# ============================================================================
# EXPORTS
# ============================================================================

# Singleton instance
cache = RedisCache()

__all__ = ['RedisCache', 'InMemoryCache', 'cache']
