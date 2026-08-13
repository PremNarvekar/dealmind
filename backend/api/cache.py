"""
In-memory Cache for Investment Memos.
In a production Kubernetes environment, this would be replaced by Redis.
"""
import time
from typing import Optional
from models.memo import InvestmentMemo

# Dictionary mapping company_name (lowercased) -> (timestamp, InvestmentMemo)
_cache: dict[str, tuple[float, InvestmentMemo]] = {}

CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours

def get_cached_memo(company_name: str) -> Optional[InvestmentMemo]:
    """Retrieve an investment memo from cache if it exists and is fresh."""
    key = company_name.strip().lower()
    if key in _cache:
        timestamp, memo = _cache[key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return memo
        else:
            del _cache[key]  # expire
    return None

def set_cached_memo(company_name: str, memo: InvestmentMemo) -> None:
    """Store an investment memo in the cache."""
    key = company_name.strip().lower()
    _cache[key] = (time.time(), memo)
