import pytest

from exchanges.coinex_network_metadata_client import (
    CoinExNetworkMetadataClient,
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
                f"http {self.status_code}"
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
        params=None,
        timeout=None,
    ):
        self.calls.append(
            {
                "url": url,
                "params": params,
                "timeout": timeout,
            }
        )
        return self._response


def valid_payload():
    return {
        "code": 0,
        "data": {
            "asset": {
                "ccy": "USDT",
                "deposit_enabled": True,
                "withdraw_enabled": True,
                "inter_transfer_enabled": True,
                "is_st": False,
            },
            "chains": [
                {
                    "chain": "BSC",
                    "min_deposit_amount": "0.2",
                    "min_withdraw_amount": "2",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "deposit_delay_minutes": 0,
                    "safe_confirmations": 12,
                    "irreversible_confirmations": 30,
                    "deflation_rate": "0",
                    "withdrawal_fee": "0.0065",
                    "withdrawal_precision": 8,
                    "memo": "",
                    "is_memo_required_for_deposit": False,
                    "explorer_asset_url": (
                        "https://bscscan.com/token/"
                        "0x55d398326f99059ff775485246999027b3197955"
                    ),
                },
                {
                    "chain": "TRC20",
                    "min_deposit_amount": "1",
                    "min_withdraw_amount": "1",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "safe_confirmations": 10,
                    "irreversible_confirmations": 20,
                    "withdrawal_fee": "5",
                    "withdrawal_precision": 6,
                    "memo": "",
                    "is_memo_required_for_deposit": False,
                    "explorer_asset_url": (
                        "https://tronscan.org/#/token20/"
                        "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                    ),
                },
            ],
        },
        "message": "OK",
    }


def test_fetch_currency_metadata_calls_coinex_endpoint():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = CoinExNetworkMetadataClient(
        session=session,
    )

    result = client.fetch_currency_metadata(
        "USDT"
    )

    assert result["asset"]["ccy"] == "USDT"
    assert len(result["chains"]) == 2

    assert session.calls == [
        {
            "url": (
                "https://api.coinex.com/"
                "v2/assets/deposit-withdraw-config"
            ),
            "params": {
                "ccy": "USDT",
            },
            "timeout": 10,
        }
    ]


def test_currency_is_normalized():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = CoinExNetworkMetadataClient(
        session=session,
    )

    client.fetch_currency_metadata(
        " usdt "
    )

    assert session.calls[0]["params"] == {
        "ccy": "USDT",
    }


def test_currency_is_required():
    client = CoinExNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(
                valid_payload()
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="currency is required",
    ):
        client.fetch_currency_metadata("")


def test_nonzero_coinex_code_fails_closed():
    session = FakeSession(
        FakeResponse(
            {
                "code": 10001,
                "data": {},
                "message": "Invalid Parameter",
            }
        )
    )

    client = CoinExNetworkMetadataClient(
        session=session,
    )

    with pytest.raises(
        RuntimeError,
        match="CoinEx metadata unavailable",
    ):
        client.fetch_currency_metadata(
            "USDT"
        )


def test_missing_data_fails_closed():
    session = FakeSession(
        FakeResponse(
            {
                "code": 0,
                "message": "OK",
            }
        )
    )

    client = CoinExNetworkMetadataClient(
        session=session,
    )

    with pytest.raises(
        RuntimeError,
        match="CoinEx metadata unavailable",
    ):
        client.fetch_currency_metadata(
            "USDT"
        )


def test_missing_chains_fails_closed():
    session = FakeSession(
        FakeResponse(
            {
                "code": 0,
                "data": {
                    "asset": {
                        "ccy": "USDT",
                    },
                },
                "message": "OK",
            }
        )
    )

    client = CoinExNetworkMetadataClient(
        session=session,
    )

    with pytest.raises(
        RuntimeError,
        match="CoinEx metadata unavailable",
    ):
        client.fetch_currency_metadata(
            "USDT"
        )


def test_client_is_read_only():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = CoinExNetworkMetadataClient(
        session=session,
    )

    result = client.describe()

    assert result["exchange_id"] == "coinex"
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
    assert result["live_transfer_submitted"] is False
