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
    ):
        self._bootstrap = bootstrap
        self._pipeline_factory = pipeline_factory

    def run(
        self,
        source_exchange_id,
        destination_exchange_id,
        scan_kwargs,
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

        result = scanner.scan(**scan_kwargs)

        record = dict(result)

        # EX-142 is verification/paper mode only.
        record["paper_only"] = True
        record["live_order_submitted"] = False

        return record
