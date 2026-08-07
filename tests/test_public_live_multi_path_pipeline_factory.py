from core.public_live_multi_path_pipeline_factory import (
    PublicLiveMultiPathPipelineFactory,
)
from core.live_multi_path_paper_scan import (
    LiveMultiPathPaperScan,
)


class FakeExchange:
    pass


def test_builds_live_multi_path_paper_pipeline():
    factory = PublicLiveMultiPathPipelineFactory()

    scanner = factory.build(
        source_exchange=FakeExchange(),
        destination_exchange=FakeExchange(),
    )

    assert isinstance(
        scanner,
        LiveMultiPathPaperScan,
    )
