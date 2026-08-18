"""
ArbOS™
EX-096
Portfolio Exposure & Concurrent Risk Engine
"""

import math


def _finite_non_negative(value, field):
    if isinstance(value, bool):
        raise ValueError(
            f"{field} must be a finite non-negative number"
        )

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(
            f"{field} must be a finite non-negative number"
        ) from None

    if not math.isfinite(number) or number < 0:
        raise ValueError(
            f"{field} must be a finite non-negative number"
        )

    return number


def _finite_positive(value, field):
    if isinstance(value, bool):
        raise ValueError(
            f"{field} must be a finite positive number"
        )

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(
            f"{field} must be a finite positive number"
        ) from None

    if not math.isfinite(number):
        raise ValueError(
            f"{field} must be a finite positive number"
        )

    if number <= 0:
        raise ValueError(
            f"{field} must be positive"
        )

    return number


def _non_negative_integer(value, field):
    if isinstance(value, bool):
        raise ValueError(
            f"{field} must be a non-negative integer"
        )

    if isinstance(value, str):
        if not value.strip().isdigit():
            raise ValueError(
                f"{field} must be a non-negative integer"
            )
        value = int(value.strip())

    if not isinstance(value, int) or value < 0:
        raise ValueError(
            f"{field} must be a non-negative integer"
        )

    return value


class PortfolioExposureConcurrentRisk:
    def evaluate(
        self,
        portfolio,
        asset,
        additional_exposure,
        required_capital,
    ):
        if portfolio is None:
            raise ValueError("portfolio is required")

        required_fields = (
            "total_capital",
            "reserved_capital",
            "max_asset_exposure",
            "open_routes",
        )

        for field in required_fields:
            if field not in portfolio:
                raise ValueError(
                    f"{field} is required"
                )

        required_capital = _finite_positive(
            required_capital,
            "required_capital",
        )
        additional_exposure = _finite_non_negative(
            additional_exposure,
            "additional_exposure",
        )

        total_capital = _finite_non_negative(
            portfolio["total_capital"],
            "total_capital",
        )
        reserved_capital = _finite_non_negative(
            portfolio["reserved_capital"],
            "reserved_capital",
        )
        max_asset_exposure = _finite_non_negative(
            portfolio["max_asset_exposure"],
            "max_asset_exposure",
        )

        if reserved_capital > total_capital:
            raise ValueError(
                "reserved_capital cannot exceed total_capital"
            )

        available_capital = total_capital - reserved_capital

        if required_capital > available_capital:
            return {
                "approved": False,
                "reason": "insufficient_unreserved_capital",
            }

        asset_exposure = portfolio.get("asset_exposure") or {}

        current_exposure = _finite_non_negative(
            asset_exposure.get(asset, 0.0),
            "current_asset_exposure",
        )

        if current_exposure + additional_exposure > max_asset_exposure:
            return {
                "approved": False,
                "reason": "asset_exposure_exceeded",
            }

        open_routes = _non_negative_integer(
            portfolio["open_routes"],
            "open_routes",
        )

        max_open_routes = portfolio.get("max_open_routes")

        if max_open_routes is not None:
            max_open_routes = _non_negative_integer(
                max_open_routes,
                "max_open_routes",
            )

            if open_routes >= max_open_routes:
                return {
                    "approved": False,
                    "reason": "concurrent_route_limit_reached",
                }

        return {
            "approved": True,
            "reason": None,
            "available_capital": available_capital,
            "projected_asset_exposure": (
                current_exposure + additional_exposure
            ),
            "open_routes": open_routes,
        }
