"""
ArbOS™
EX-217
WEEX Verification Adapter

Normalizes WEEX public order-book and coin/network
metadata into stable ArbOS™ verification structures.

Read-only and paper-safe.
No transfers.
No live orders.
"""


class WeexVerificationAdapter:
    EXCHANGE = "weex"

    def __init__(
        self,
        network_normalizer=None,
    ):
        self._network_normalizer = (
            network_normalizer
        )

    def normalize_depth(
        self,
        depth,
    ):
        if not depth.get(
            "fetch_complete",
            False,
        ):
            return {
                "exchange": self.EXCHANGE,
                "available": False,
                "reason": depth.get(
                    "reason",
                    "depth_unavailable",
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        symbol = str(
            depth.get(
                "symbol",
                "",
            )
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        bids = self._normalize_levels(
            depth.get("bids", [])
        )

        asks = self._normalize_levels(
            depth.get("asks", [])
        )

        return {
            "exchange": self.EXCHANGE,
            "available": True,
            "symbol": symbol,
            "last_update_id": depth.get(
                "last_update_id"
            ),
            "best_bid": (
                bids[0]["price"]
                if bids
                else None
            ),
            "best_ask": (
                asks[0]["price"]
                if asks
                else None
            ),
            "bids": bids,
            "asks": asks,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def normalize_coin(
        self,
        coin_data,
    ):
        coin = str(
            coin_data.get(
                "coin",
                "",
            )
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        network_list = coin_data.get(
            "networkList",
            [],
        )

        if not isinstance(
            network_list,
            list,
        ):
            raise ValueError(
                "networkList must be a list"
            )

        networks = []

        for network_data in network_list:
            raw_network = str(
                network_data.get(
                    "network",
                    "",
                )
                or ""
            ).strip()

            network = raw_network

            if (
                self._network_normalizer
                is not None
                and raw_network
            ):
                network = (
                    self._network_normalizer
                    .normalize(
                        raw_network
                    )
                )

            networks.append({
                "network": network,
                "raw_network": raw_network,
                "is_default": bool(
                    network_data.get(
                        "isDefault",
                        False,
                    )
                ),
                "deposit_enabled": bool(
                    network_data.get(
                        "depositEnable",
                        False,
                    )
                ),
                "withdraw_enabled": bool(
                    network_data.get(
                        "withdrawEnable",
                        False,
                    )
                ),
                "withdraw_fee": (
                    self._optional_float(
                        network_data.get(
                            "withdrawFee"
                        )
                    )
                ),
                "withdraw_min": (
                    self._optional_float(
                        network_data.get(
                            "withdrawMin"
                        )
                    )
                ),
                "withdraw_integer_multiple": (
                    self._optional_float(
                        network_data.get(
                            "withdrawIntegerMultiple"
                        )
                    )
                ),
                "min_confirmations": (
                    self._optional_int(
                        network_data.get(
                            "minConfirm"
                        )
                    )
                ),
            })

        return {
            "exchange": self.EXCHANGE,
            "coin": coin,
            "deposit_enabled": bool(
                coin_data.get(
                    "depositAllEnable",
                    False,
                )
            ),
            "withdraw_enabled": bool(
                coin_data.get(
                    "withdrawAllEnable",
                    False,
                )
            ),
            "networks": networks,
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _normalize_levels(
        levels,
    ):
        normalized = []

        for level in levels:
            if (
                not isinstance(
                    level,
                    (list, tuple),
                )
                or len(level) < 2
            ):
                continue

            normalized.append({
                "price": float(
                    level[0]
                ),
                "quantity": float(
                    level[1]
                ),
            })

        return normalized

    @staticmethod
    def _optional_float(
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        return float(value)

    @staticmethod
    def _optional_int(
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        return int(value)
