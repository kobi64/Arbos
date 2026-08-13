import pytest

from core.sharpe_spot_transfer_api_client import (
    SharpeSpotTransferAPIClient,
)


class FakeResponse:
    def __init__(
        self,
        payload,
        status_code=200,
    ):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(
                f"HTTP {self.status_code}"
            )

    def json(self):
        return self._payload


class FakeSession:
    def __init__(
        self,
        response,
    ):
        self._response = response
        self.calls = []

    def get(
        self,
        url,
        params,
        timeout,
    ):
        self.calls.append({
            "url": url,
            "params": dict(params),
            "timeout": timeout,
        })

        return self._response


def payload():
    return {
        "data": [
            {
                "coin": "COTI",
                "buyExchange": "kucoin",
                "sellExchange": "bitget",
            },
        ],
        "meta": {
            "kind": "cex-spot-transfer",
            "status": "ok",
            "generatedAt": (
                "2026-08-13T12:39:17.739Z"
            ),
            "updatedAt": (
                "2026-08-13T12:39:17.702Z"
            ),
            "stale": False,
            "freshnessSlaSeconds": 3600,
            "source": "live",
            "notionalUsd": 300,
            "rowCount": 1,
        },
        "pagination": {
            "cursor": None,
            "has_more": False,
            "total": 1,
        },
    }


def test_fetches_public_sharpe_spot_transfer_results():
    session = FakeSession(
        FakeResponse(
            payload()
        )
    )

    client = SharpeSpotTransferAPIClient(
        session=session,
        timeout_seconds=15,
    )

    result = client.fetch(
        notional_usd=300,
        limit=10,
    )

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "source"
    ] == "sharpe"

    assert result[
        "kind"
    ] == "cex-spot-transfer"

    assert result[
        "result_count"
    ] == 1

    assert session.calls[0][
        "url"
    ] == (
        "https://www.sharpe.ai/"
        "api/arbitrage/cex-spot-transfer"
    )

    assert session.calls[0][
        "params"
    ] == {
        "notional": 300.0,
        "limit": 10,
    }

    assert session.calls[0][
        "timeout"
    ] == 15.0


def test_preserves_sharpe_freshness_metadata():
    client = SharpeSpotTransferAPIClient(
        session=FakeSession(
            FakeResponse(
                payload()
            )
        )
    )

    result = client.fetch(
        notional_usd=300,
        limit=10,
    )

    assert result[
        "generated_at"
    ] == (
        "2026-08-13T12:39:17.739Z"
    )

    assert result[
        "updated_at"
    ] == (
        "2026-08-13T12:39:17.702Z"
    )

    assert result[
        "stale"
    ] is False

    assert result[
        "freshness_sla_seconds"
    ] == 3600


def test_empty_spot_result_is_successful_fetch():
    value = payload()
    value["data"] = []
    value["meta"]["rowCount"] = 0
    value["pagination"]["total"] = 0

    client = SharpeSpotTransferAPIClient(
        session=FakeSession(
            FakeResponse(
                value
            )
        )
    )

    result = client.fetch(
        notional_usd=300,
        limit=10,
    )

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "result_count"
    ] == 0

    assert result[
        "results"
    ] == []


def test_rejects_non_spot_transfer_payload_kind():
    value = payload()

    value["meta"]["kind"] = (
        "perpetual-arbitrage"
    )

    client = SharpeSpotTransferAPIClient(
        session=FakeSession(
            FakeResponse(
                value
            )
        )
    )

    result = client.fetch(
        notional_usd=300,
        limit=10,
    )

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "reason"
    ] == "non_spot_transfer_payload"

    assert result[
        "results"
    ] == []


def test_invalid_payload_returns_failed_result():
    client = SharpeSpotTransferAPIClient(
        session=FakeSession(
            FakeResponse({
                "unexpected": [],
            })
        )
    )

    result = client.fetch(
        notional_usd=300,
        limit=10,
    )

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "results"
    ] == []


def test_http_failure_returns_failed_result():
    client = SharpeSpotTransferAPIClient(
        session=FakeSession(
            FakeResponse(
                {},
                status_code=500,
            )
        )
    )

    result = client.fetch(
        notional_usd=300,
        limit=10,
    )

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "results"
    ] == []


def test_notional_must_be_positive():
    client = SharpeSpotTransferAPIClient(
        session=FakeSession(
            FakeResponse(
                payload()
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="notional_usd must be positive",
    ):
        client.fetch(
            notional_usd=0,
            limit=10,
        )


def test_limit_must_be_positive():
    client = SharpeSpotTransferAPIClient(
        session=FakeSession(
            FakeResponse(
                payload()
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="limit must be positive",
    ):
        client.fetch(
            notional_usd=300,
            limit=0,
        )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        SharpeSpotTransferAPIClient(
            session=FakeSession(
                FakeResponse({})
            ),
            timeout_seconds=0,
        )


def test_client_is_paper_safe():
    client = SharpeSpotTransferAPIClient(
        session=FakeSession(
            FakeResponse(
                payload()
            )
        )
    )

    result = client.fetch(
        notional_usd=300,
        limit=10,
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
