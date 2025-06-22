"""
Footy-Brain v5 API Server Dependencies
FastAPI dependency injection for authentication, database sessions, and common utilities.
"""

import os
import jwt
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime, timedelta

import asyncpg
import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Security
security = HTTPBearer()

# Global connections (will be initialized in main.py)
db_engine = None
redis_client = None
session_maker = None


class DatabaseManager:
    """Database connection manager for async operations."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_maker = None
        
    async def initialize(self):
        """Initialize database engine and session maker."""
        # Convert PostgreSQL URL to async version
        async_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        self.engine = create_async_engine(
            async_url,
            poolclass=NullPool,  # Use NullPool for simplicity in development
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
        )
        
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        if not self.session_maker:
            raise RuntimeError("Database not initialized")
            
        async with self.session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


class RedisManager:
    """Redis connection manager for caching and pub/sub."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client = None
        
    async def initialize(self):
        """Initialize Redis client."""
        self.client = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
    async def get_client(self) -> redis.Redis:
        """Get Redis client."""
        if not self.client:
            raise RuntimeError("Redis not initialized")
        return self.client
        
    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()


# Global managers (will be initialized in main.py)
db_manager: Optional[DatabaseManager] = None
redis_manager: Optional[RedisManager] = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_session)):
            # Use db session
    """
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    async for session in db_manager.get_session():
        yield session


async def get_redis_client() -> redis.Redis:
    """
    FastAPI dependency to get Redis client.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(redis_client: redis.Redis = Depends(get_redis_client)):
            # Use Redis client
    """
    if not redis_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis not available"
        )
    
    return await redis_manager.get_client()


async def get_raw_db_connection() -> asyncpg.Connection:
    """
    Get raw asyncpg connection for direct SQL operations.
    Useful for TimescaleDB-specific operations.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: asyncpg.Connection = Depends(get_raw_db_connection)):
            # Use raw connection
    """
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    # Extract connection details from URL
    database_url = db_manager.database_url
    
    try:
        connection = await asyncpg.connect(database_url)
        try:
            yield connection
        finally:
            await connection.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    
    secret_key = os.getenv('JWT_SECRET', 'footy_jwt_secret_2024')
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token data
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        secret_key = os.getenv('JWT_SECRET', 'footy_jwt_secret_2024')
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    Usage:
        @app.get("/protected")
        async def protected(user: dict = Depends(get_current_user)):
            # Use user data
    """
    # TODO: Implement proper JWT token validation
    
    # Verify the token
    payload = verify_token(credentials.credentials)
    
    # Extract user information from token
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Fetch user details from database
    # For now, return basic user info from token
    return {
        "user_id": user_id,
        "username": payload.get("username"),
        "email": payload.get("email"),
        "roles": payload.get("roles", [])
    }


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to get current user if authenticated, None otherwise.
    Useful for endpoints that work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_roles(required_roles: list):
    """
    Dependency factory to require specific roles.
    
    Usage:
        @app.get("/admin")
        async def admin_endpoint(user: dict = Depends(require_roles(["admin"]))):
            # Only admin users can access
    """
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_roles = user.get("roles", [])
        
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        
        return user
    
    return role_checker


class RateLimiter:
    """Simple rate limiter using Redis."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def is_allowed(self, key: str, redis_client: redis.Redis) -> bool:
        """Check if request is allowed under rate limit."""
        try:
            current = await redis_client.get(f"rate_limit:{key}")
            
            if current is None:
                # First request in window
                await redis_client.setex(f"rate_limit:{key}", self.window_seconds, 1)
                return True
            
            if int(current) >= self.max_requests:
                return False
            
            # Increment counter
            await redis_client.incr(f"rate_limit:{key}")
            return True
            
        except Exception:
            # If Redis is down, allow the request
            return True


def create_rate_limiter(max_requests: int, window_seconds: int):
    """
    Create a rate limiter dependency.
    
    Usage:
        rate_limit = create_rate_limiter(100, 60)  # 100 requests per minute
        
        @app.get("/api/endpoint")
        async def endpoint(rate_check = Depends(rate_limit)):
            # Endpoint logic
    """
    limiter = RateLimiter(max_requests, window_seconds)
    
    async def rate_limit_dependency(
        request,
        redis_client: redis.Redis = Depends(get_redis_client),
        user: Optional[Dict[str, Any]] = Depends(get_optional_user)
    ):
        # Use user ID if authenticated, otherwise use IP address
        if user:
            key = f"user:{user['user_id']}"
        else:
            key = f"ip:{request.client.host}"
        
        if not await limiter.is_allowed(key, redis_client):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
    
    return rate_limit_dependency


# Common rate limiters
api_rate_limit = create_rate_limiter(1000, 60)  # 1000 requests per minute
auth_rate_limit = create_rate_limiter(10, 60)   # 10 auth attempts per minute
