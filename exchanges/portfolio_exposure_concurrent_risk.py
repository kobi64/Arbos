"""
ArbOS™
EX-096
Portfolio Exposure & Concurrent Risk Engine
"""


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

        if required_capital <= 0:
            raise ValueError("required_capital must be positive")

        total_capital = float(portfolio.get("total_capital", 0.0))
        reserved_capital = float(portfolio.get("reserved_capital", 0.0))
        available_capital = total_capital - reserved_capital

        if required_capital > available_capital:
            return {
                "approved": False,
                "reason": "insufficient_unreserved_capital",
            }

        asset_exposure = portfolio.get("asset_exposure") or {}
        current_exposure = float(asset_exposure.get(asset, 0.0))
        max_asset_exposure = float(portfolio.get("max_asset_exposure", 1.0))

        if current_exposure + additional_exposure > max_asset_exposure:
            return {
                "approved": False,
                "reason": "asset_exposure_exceeded",
            }

        open_routes = int(portfolio.get("open_routes", 0))
        max_open_routes = portfolio.get("max_open_routes")

        if (
            max_open_routes is not None
            and open_routes >= int(max_open_routes)
        ):
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
