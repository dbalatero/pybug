"""Temporary reservations for a bank of parcel lockers."""

from collections import deque
from dataclasses import dataclass
import heapq
from typing import Dict, Optional


@dataclass(frozen=True)
class Hold:
    customer: str
    locker: int
    expires_at: int


class LockerBank:
    def __init__(self, capacity: int, hold_minutes: int = 10):
        if capacity < 1 or hold_minutes < 1:
            raise ValueError("capacity and hold_minutes must be positive")
        self._duration = hold_minutes
        self._now = 0
        self._free = list(range(1, capacity + 1))
        self._waiting = deque()
        self._holds: Dict[str, Hold] = {}
        self._deadlines = []

    def request(self, customer: str) -> Optional[Hold]:
        """Return the customer's hold, or queue the customer if full."""
        if customer in self._holds:
            return self._holds[customer]
        if self._free:
            return self._assign(customer)
        if customer not in self._waiting:
            self._waiting.append(customer)
        return None

    def lookup(self, customer: str) -> Optional[Hold]:
        return self._holds.get(customer)

    def cancel(self, customer: str) -> None:
        if customer in self._holds:
            self._release(customer)
        elif customer in self._waiting:
            self._waiting.remove(customer)

    def advance(self, minute: int) -> None:
        """Process deadlines in order, including promotions during a time jump."""
        if minute < self._now:
            raise ValueError("time cannot move backwards")
        while self._deadlines and self._deadlines[0][0] <= minute:
            self._now, customer = heapq.heappop(self._deadlines)
            if customer in self._holds:
                self._release(customer)
        self._now = minute

    def _assign(self, customer: str) -> Hold:
        locker = heapq.heappop(self._free)
        hold = Hold(customer, locker, self._now + self._duration)
        self._holds[customer] = hold
        heapq.heappush(self._deadlines, (hold.expires_at, customer))
        return hold

    def _release(self, customer: str) -> None:
        hold = self._holds.pop(customer)
        heapq.heappush(self._free, hold.locker)
        if self._waiting:
            self._assign(self._waiting.popleft())
