import json
import time
from typing import Dict, Any, Optional

class AdaptiveTokenRateLimiterClient:
    """
    Production-grade token-bucket concurrency rate limiter.
    Enforces RPM and TPM sliding limits with dynamic millisecond backoff calculations.
    """
    def __init__(self, max_tokens_per_min: int = 60000, max_requests_per_min: int = 500):
        self.max_tpm = max_tokens_per_min
        self.max_rpm = max_requests_per_min
        self.available_tokens = max_tokens_per_min
        self.available_requests = max_requests_per_min
        self.last_refill = time.time()

    def acquire_token_permit(self, requested_tokens: int = 2400) -> Dict[str, Any]:
        now = time.time()
        elapsed = now - self.last_refill
        # Refill tokens based on elapsed seconds
        refill_t = (self.max_tpm / 60.0) * elapsed
        self.available_tokens = min(self.max_tpm, self.available_tokens + refill_t)
        self.last_refill = now

        if self.available_tokens >= requested_tokens and self.available_requests >= 1:
            self.available_tokens -= requested_tokens
            self.available_requests -= 1
            return {
                "verdict": "PERMIT_GRANTED",
                "allocated_tokens": requested_tokens,
                "remaining_tokens_budget": round(self.available_tokens, 1),
                "wait_backoff_ms": 0,
                "concurrency_pressure": round((1.0 - (self.available_tokens / self.max_tpm)) * 100, 1)
            }
        else:
            deficit = requested_tokens - self.available_tokens
            wait_sec = deficit / (self.max_tpm / 60.0)
            return {
                "verdict": "RATE_LIMIT_BACKOFF_REQUIRED",
                "allocated_tokens": 0,
                "remaining_tokens_budget": round(self.available_tokens, 1),
                "wait_backoff_ms": int(wait_sec * 1000) + 150,
                "concurrency_pressure": 100.0
            }
