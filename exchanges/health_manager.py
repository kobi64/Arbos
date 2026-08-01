"""
ArbOS™
EX-002
Exchange Health Manager
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExchangeHealth:

    exchange: str

    online: bool = False

    authenticated: bool = False

    rest_latency_ms: float = 0.0

    websocket_latency_ms: float = 0.0

    error_rate: float = 0.0

    maintenance: bool = False

    last_check: datetime | None = None

    health_score: float = 0.0


class HealthManager:

    def calculate_score(
        self,
        health: ExchangeHealth
    ) -> float:

        score = 100.0

        if not health.online:
            score -= 50

        if not health.authenticated:
            score -= 20

        score -= min(health.error_rate * 100, 20)

        if health.rest_latency_ms > 500:
            score -= 10

        if health.websocket_latency_ms > 500:
            score -= 10

        if health.maintenance:
            score -= 50

        score = max(0.0, score)

        health.health_score = score

        health.last_check = datetime.utcnow()

        return score

    def status(
        self,
        health: ExchangeHealth
    ) -> str:

        if health.health_score >= 90:
            return "HEALTHY"

        if health.health_score >= 70:
            return "WARNING"

        if health.health_score >= 50:
            return "DEGRADED"

        return "OFFLINE"
