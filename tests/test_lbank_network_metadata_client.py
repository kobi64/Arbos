from exchanges.lbank_network_metadata_client import (
    LBankNetworkMetadataClient,
)


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "result": "true",
            "data": [
                {
                    "assetCode": "usdt",
                    "chainName": "erc20",
                    "canDeposit": True,
                    "canDraw": True,
                    "canStationDraw": True,
                    "contractInfo": (
                        "0xdac17f958d2ee523a2206206994597c13d831ec7"
                    ),
                    "hasMemo": False,
                    "assetFee": {
                        "feeAmt": "1",
                        "feeCode": "usdt",
                        "feeRate": "0",
                        "minAmt": "10",
                        "minDepositAmt": "0.0001",
                        "depositFee": "0",
                    },
                }
            ],
        }


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(
            {
                "url": url,
                "params": params,
                "timeout": timeout,
            }
        )
        return FakeResponse()


def test_fetches_public_asset_metadata():
    session = FakeSession()

    client = LBankNetworkMetadataClient(
        session=session,
    )

    result = client.fetch_asset_metadata(
        "USDT"
    )

    assert result["fetch_complete"] is True
    assert result["asset"] == "USDT"
    assert len(result["networks"]) == 1

    assert session.calls[0]["params"] == {
        "assetCode": "usdt",
    }


def test_preserves_network_identity_fields():
    client = LBankNetworkMetadataClient(
        session=FakeSession(),
    )

    result = client.fetch_asset_metadata(
        "USDT"
    )

    network = result["networks"][0]

    assert network["chainName"] == "erc20"
    assert network["canDeposit"] is True
    assert network["canDraw"] is True
    assert network["contractInfo"] == (
        "0xdac17f958d2ee523a2206206994597c13d831ec7"
    )
    assert network["hasMemo"] is False


def test_preserves_fee_metadata():
    client = LBankNetworkMetadataClient(
        session=FakeSession(),
    )

    result = client.fetch_asset_metadata(
        "USDT"
    )

    fee = result["networks"][0]["assetFee"]

    assert fee["minAmt"] == "10"
    assert fee["feeAmt"] == "1"
    assert fee["minDepositAmt"] == "0.0001"


def test_asset_is_required():
    client = LBankNetworkMetadataClient(
        session=FakeSession(),
    )

    try:
        client.fetch_asset_metadata("")
    except ValueError as exc:
        assert "asset is required" in str(exc)
    else:
        raise AssertionError(
            "expected ValueError"
        )


def test_client_is_read_only():
    client = LBankNetworkMetadataClient(
        session=FakeSession(),
    )

    result = client.fetch_asset_metadata(
        "USDT"
    )

    assert result["paper_only"] is True
    assert result["live_transfer_submitted"] is False
