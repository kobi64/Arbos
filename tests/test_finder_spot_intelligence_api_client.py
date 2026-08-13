import pytest

from core.finder_spot_intelligence_api_client import (
    FinderSpotIntelligenceAPIClient,
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
    def __init__(self, response):
        self._response = response
        self.calls = []

    def get(
        self,
        url,
        timeout,
        headers=None,
    ):
        self.calls.append({
            "url": url,
            "timeout": timeout,
            "headers": headers,
        })

        return self._response


def payload():
    return {
        "items": [
            {
                "token": "LUNC",
                "quote": "USDT",
                "buyEx": "Poloniex",
                "sellEx": "Kucoin",
                "buyP": 0.00003936,
                "sellP": 0.00004928,
                "spread": 24.8763,
                "profit": 49.331,
                "cls": "veryhigh",
            },
            {
                "token": "GALA",
                "quote": "USDTM",
                "buyEx": "Kucoin",
                "sellEx": "Poloniex",
                "buyP": 0.001656,
                "sellP": 0.001936,
                "spread": 16.6,
                "profit": 11.9,
                "cls": "veryhigh",
            },
        ],
    }


def test_fetches_public_finder_results():
    session = FakeSession(
        FakeResponse(payload())
    )

    client = FinderSpotIntelligenceAPIClient(
        session=session,
        timeout_seconds=15,
    )

    result = client.fetch()

    assert result["fetch_complete"] is True
    assert result["source"] == "finder"
    assert result["result_count"] == 1

    assert result["results"][0][
        "token"
    ] == "LUNC"

    assert session.calls[0]["url"] == (
        "https://finder-arbitrage.com/"
        "api/landing-ticker"
    )

    assert session.calls[0][
        "timeout"
    ] == 15.0


def test_nonstandard_quotes_are_filtered():
    client = FinderSpotIntelligenceAPIClient(
        session=FakeSession(
            FakeResponse(payload())
        )
    )

    result = client.fetch()

    assert result["result_count"] == 1

    assert result[
        "filtered_non_usdt_count"
    ] == 1


def test_empty_items_is_successful_fetch():
    client = FinderSpotIntelligenceAPIClient(
        session=FakeSession(
            FakeResponse({
                "items": [],
            })
        )
    )

    result = client.fetch()

    assert result["fetch_complete"] is True
    assert result["result_count"] == 0
    assert result["results"] == []


def test_invalid_payload_returns_failed_result():
    client = FinderSpotIntelligenceAPIClient(
        session=FakeSession(
            FakeResponse({
                "unexpected": [],
            })
        )
    )

    result = client.fetch()

    assert result["fetch_complete"] is False
    assert result["results"] == []


def test_http_failure_returns_failed_result():
    client = FinderSpotIntelligenceAPIClient(
        session=FakeSession(
            FakeResponse(
                {},
                status_code=500,
            )
        )
    )

    result = client.fetch()

    assert result["fetch_complete"] is False
    assert result["results"] == []


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        FinderSpotIntelligenceAPIClient(
            session=FakeSession(
                FakeResponse({})
            ),
            timeout_seconds=0,
        )


def test_client_is_paper_safe():
    client = FinderSpotIntelligenceAPIClient(
        session=FakeSession(
            FakeResponse(payload())
        )
    )

    result = client.fetch()

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False
