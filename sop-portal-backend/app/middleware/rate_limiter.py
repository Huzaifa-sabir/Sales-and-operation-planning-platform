"""
Rate Limiting Middleware
Prevents API abuse by limiting requests per user/IP
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse
    Tracks requests per minute for each user/IP combination
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # Cleanup old entries every 60 seconds
        self.last_cleanup = datetime.utcnow()

    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for client (IP + User if authenticated)"""
        # Get IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0]
        else:
            ip = request.client.host if request.client else "unknown"

        # Get user ID from token if available
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # In production, decode token to get user ID
            # For now, use partial token as identifier
            token_part = auth_header[7:20]  # First few chars of token
            return f"{ip}:{token_part}"

        return ip

    def _cleanup_old_entries(self):
        """Remove request timestamps older than 1 minute"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=1)

        for key in list(self.request_counts.keys()):
            # Filter out old timestamps
            self.request_counts[key] = [
                timestamp for timestamp in self.request_counts[key]
                if timestamp > cutoff_time
            ]

            # Remove key if no recent requests
            if not self.request_counts[key]:
                del self.request_counts[key]

        self.last_cleanup = datetime.utcnow()

    def _is_rate_limited(self, identifier: str) -> Tuple[bool, int]:
        """
        Check if client has exceeded rate limit

        Returns:
            (is_limited, current_count)
        """
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)

        # Get recent requests
        recent_requests = [
            timestamp for timestamp in self.request_counts[identifier]
            if timestamp > one_minute_ago
        ]

        # Update list
        self.request_counts[identifier] = recent_requests

        # Check if limit exceeded
        current_count = len(recent_requests)
        is_limited = current_count >= self.requests_per_minute

        return is_limited, current_count

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/api/docs", "/api/openapi.json"]:
            return await call_next(request)

        # Periodic cleanup
        if (datetime.utcnow() - self.last_cleanup).seconds > self.cleanup_interval:
            self._cleanup_old_entries()

        # Get client identifier
        identifier = self._get_client_identifier(request)

        # Check rate limit
        is_limited, current_count = self._is_rate_limited(identifier)

        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute allowed. Try again later.",
                headers={"Retry-After": "60"}
            )

        # Record this request
        self.request_counts[identifier].append(datetime.utcnow())

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute - current_count - 1)
        response.headers["X-RateLimit-Reset"] = str(60)  # seconds until reset

        return response
