import time
from typing import Any, Optional, Dict


class SimpleTTLCache:
    def __init__(self, default_ttl: int = 30):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        item = self.cache.get(key)
        if not item:
            return None
        if time.time() > item["expiry"]:
            del self.cache[key]
            return None
        return item["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expiry = time.time() + (ttl or self.default_ttl)
        self.cache[key] = {"value": value, "expiry": expiry}

    def clear(self):
        self.cache.clear()


memory_cache = SimpleTTLCache(default_ttl=30)
