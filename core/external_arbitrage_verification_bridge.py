"""
ArbOS™
EX-211
External Arbitrage Verification Bridge

Bridges normalized external arbitrage candidates into the
existing ArbOS™ public live-paper verification pipeline.

External source claims never override ArbOS™ verification.

Paper-safe infrastructure only.
No live orders.
"""


class ExternalArbitrageVerificationBridge:
    def __init__(
        self,
        runner,
        tracker,
    ):
        if runner is None:
            raise ValueError(
                "runner is required"
            )

        if tracker is None:
            raise ValueError(
                "tracker is required"
            )

        self._runner = runner
        self._tracker = tracker

    def verify(
        self,
        candidate,
        starting_usdt_value,
        source_fee_rate,
        destination_fee_rate,
        max_slippage_percent=0.5,
        minimum_profit_percent=0.0,
    ):
        if candidate is None:
            raise ValueError(
                "candidate is required"
            )

        opportunity_key = str(
            candidate.get(
                "opportunity_key",
                "",
            )
            or ""
        ).strip()

        if not opportunity_key:
            raise ValueError(
                "opportunity_key is required"
            )

        coin = str(
            candidate.get(
                "coin",
                "",
            )
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        buy_exchange = str(
            candidate.get(
                "buy_exchange",
                "",
            )
            or ""
        ).strip().lower()

        if not buy_exchange:
            raise ValueError(
                "buy_exchange is required"
            )

        sell_exchange = str(
            candidate.get(
                "sell_exchange",
                "",
            )
            or ""
        ).strip().lower()

        if not sell_exchange:
            raise ValueError(
                "sell_exchange is required"
            )

        starting_usdt_value = float(
            starting_usdt_value
        )

        if starting_usdt_value <= 0:
            raise ValueError(
                "starting_usdt_value must be positive"
            )

        runner_result = self._runner.run(
            source_exchange_id=(
                buy_exchange
            ),
            destination_exchange_id=(
                sell_exchange
            ),
            prepare_kwargs={
                "coin_asset": coin,
                "starting_usdt_value": (
                    starting_usdt_value
                ),
                "source_fee_rate": float(
                    source_fee_rate
                ),
                "destination_fee_rate": float(
                    destination_fee_rate
                ),
                "max_slippage_percent": float(
                    max_slippage_percent
                ),
                "minimum_profit_percent": float(
                    minimum_profit_percent
                ),
            },
        )

        best_cross_exchange = (
            runner_result.get(
                "best_cross_exchange"
            )
        )

        verified = False
        executable = False
        verified_net_profit = None
        verified_net_profit_percent = None
        verification_reason = None

        if (
            runner_result.get(
                "scan_complete"
            )
            is False
        ):
            verification_reason = (
                runner_result.get(
                    "reason",
                    "verification_scan_failed",
                )
            )

        elif (
            isinstance(
                best_cross_exchange,
                dict,
            )
            and best_cross_exchange.get(
                "executable"
            )
            is True
        ):
            verified = True
            executable = True

            verified_net_profit = (
                best_cross_exchange.get(
                    "net_profit"
                )
            )

            verified_net_profit_percent = (
                best_cross_exchange.get(
                    "net_profit_percent"
                )
            )

        else:
            if isinstance(
                best_cross_exchange,
                dict,
            ):
                verification_reason = (
                    best_cross_exchange.get(
                        "reason",
                        "route_not_executable",
                    )
                )
            else:
                rejected = (
                    runner_result.get(
                        "rejected_cross_exchange"
                    )
                    or []
                )

                if rejected:
                    verification_reason = (
                        rejected[0].get(
                            "reason",
                            "no_verified_cross_exchange_route",
                        )
                    )
                else:
                    verification_reason = (
                        "no_verified_cross_exchange_route"
                    )

        self._tracker.record_verification(
            opportunity_key=(
                opportunity_key
            ),
            verified=verified,
            executable=executable,
        )

        return {
            **candidate,
            "arbos_verified": verified,
            "executable": executable,
            "verification_required": False,
            "verification_reason": (
                verification_reason
            ),
            "verified_net_profit": (
                verified_net_profit
            ),
            "verified_net_profit_percent": (
                verified_net_profit_percent
            ),
            "verification_result": (
                runner_result
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
