"""
ArbOS™
EX-142
Public Live Multi-Path Verification Runner
"""


class PublicLiveMultiPathVerificationRunner:
    def __init__(
        self,
        bootstrap,
        pipeline_factory,
        input_preparer_factory=None,
    ):
        self._bootstrap = bootstrap
        self._pipeline_factory = pipeline_factory
        self._input_preparer_factory = input_preparer_factory

    def run(
        self,
        source_exchange_id,
        destination_exchange_id,
        scan_kwargs=None,
        prepare_kwargs=None,
    ):
        if not source_exchange_id:
            raise ValueError(
                "source_exchange_id is required"
            )

        if not destination_exchange_id:
            raise ValueError(
                "destination_exchange_id is required"
            )

        source_exchange = self._bootstrap.create(
            source_exchange_id
        )

        destination_exchange = self._bootstrap.create(
            destination_exchange_id
        )

        scanner = self._pipeline_factory.build(
            source_exchange=source_exchange,
            destination_exchange=destination_exchange,
        )

        if prepare_kwargs is not None:
            if self._input_preparer_factory is None:
                raise ValueError(
                    "input_preparer_factory is required"
                )

            preparer = self._input_preparer_factory(
                source_exchange=source_exchange,
                destination_exchange=destination_exchange,
            )

            prepared = preparer.prepare(
                source_exchange_id=source_exchange_id,
                destination_exchange_id=destination_exchange_id,
                **prepare_kwargs,
            )

            starting_value = float(
                prepare_kwargs["starting_usdt_value"]
            )

            source_fee_rate = float(
                prepare_kwargs["source_fee_rate"]
            )

            scan_kwargs = {
                "markets": prepared["markets"],
                "quote_asset": "USDT",
                "coin_asset": prepared["coin_asset"],
                "starting_value": starting_value,
                "fee_rate": source_fee_rate,
                "destination_fee_rate": float(
                    prepare_kwargs.get(
                        "destination_fee_rate",
                        source_fee_rate,
                    )
                ),
                "max_slippage_percent": float(
                    prepare_kwargs.get(
                        "max_slippage_percent",
                        0.5,
                    )
                ),
                "cross_exchange_generate_kwargs": {
                    "source_exchange": (
                        source_exchange_id
                    ),
                    "destination_exchange": (
                        destination_exchange_id
                    ),
                    "coin_asset": (
                        prepared["coin_asset"]
                    ),
                    "coin_amount": (
                        prepared["coin_amount"]
                    ),
                    "source_networks": (
                        prepared["source_networks"]
                    ),
                    "destination_networks": (
                        prepared[
                            "destination_networks"
                        ]
                    ),
                    "bridge_quotes": (
                        prepared["bridge_quotes"]
                    ),
                },
            }

        if scan_kwargs is None:
            raise ValueError(
                "scan_kwargs or prepare_kwargs is required"
            )

        result = scanner.scan(**scan_kwargs)

        record = dict(result)

        record["paper_only"] = True
        record["live_order_submitted"] = False

        return record
