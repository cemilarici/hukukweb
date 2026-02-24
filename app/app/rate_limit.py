from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class Window:
    hits: deque[float] = field(default_factory=deque)


class IPRateLimiter:
    def __init__(self, max_hits: int = 5, window_seconds: int = 300) -> None:
        self.max_hits = max_hits
        self.window_seconds = window_seconds
        self._store: dict[str, Window] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        window = self._store.setdefault(key, Window())
        while window.hits and now - window.hits[0] > self.window_seconds:
            window.hits.popleft()
        if len(window.hits) >= self.max_hits:
            return False
        window.hits.append(now)
        return True
