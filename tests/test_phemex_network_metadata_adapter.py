import pytest

from exchanges.phemex_network_metadata_adapter import (
    PhemexNetworkMetadataAdapter,
)


class FakeClient:
    def fetch_networks(
        self,
        currency,
    ):
        return {
            "code": 0,
            "msg": "OK",
            "data": {
                "USDT": [
                    {
                        "currencyCode": 3,
                        "currencyName": "USDT",
                        "chainName": "TRX",
                        "chainTxUrl": (
                            "https://tronscan.org/"
                            "#/transaction/"
                        ),
                        "chainId": 11,
                        "displayName": "TRC20",
                        "displayNetwork": "TRX",
                        "inUse": True,
                        "isMetamask": 0,
                        "domainType": 0,
                        "domainSuffix": None,
                        "permanentlyClosed": 0,
                    },
                    {
                        "currencyCode": 3,
                        "currencyName": "USDT",
                        "chainName": "FTM",
                        "chainTxUrl": (
                            "https://ftmscan.com/tx/"
                        ),
                        "chainId": 46,
                        "displayName": "Fantom",
                        "displayNetwork": "FTM",
                        "inUse": True,
                        "isMetamask": 1,
                        "domainType": 0,
                        "domainSuffix": None,
                        "permanentlyClosed": 1,
                    },
                ],
            },
        }


class FailedClient:
    def fetch_networks(
        self,
        currency,
    ):
        raise RuntimeError(
            "Phemex network metadata unavailable"
        )


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        PhemexNetworkMetadataAdapter(
            client=None,
        )


def test_describes_phemex_networks():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "transfer_verification_available"
    ] is False

    assert len(
        result["networks"]
    ) == 2

    trx = result["networks"][0]

    assert trx["network"] == "TRX"
    assert trx["display_name"] == "TRC20"
    assert trx["display_network"] == "TRX"
    assert trx["chain_id"] == 11
    assert trx["in_use"] is True
    assert trx[
        "permanently_closed"
    ] is False


def test_permanently_closed_network_is_preserved():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    ftm = result["networks"][1]

    assert ftm["network"] == "FTM"
    assert ftm[
        "permanently_closed"
    ] is True

    assert ftm[
        "operational"
    ] is False


def test_operational_network_requires_in_use_and_not_closed():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    trx = result["networks"][0]

    assert trx[
        "operational"
    ] is True


def test_transfer_specific_fields_remain_unknown():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    trx = result["networks"][0]

    assert trx[
        "deposit_enabled"
    ] is None

    assert trx[
        "withdraw_enabled"
    ] is None

    assert trx[
        "minimum_deposit"
    ] is None

    assert trx[
        "minimum_withdrawal"
    ] is None

    assert trx[
        "withdraw_fee"
    ] is None

    assert trx[
        "confirmations"
    ] is None


def test_currency_is_normalized():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_failed_fetch_fails_closed():
    adapter = PhemexNetworkMetadataAdapter(
        client=FailedClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "transfer_verification_available"
    ] is False

    assert result["networks"] == []


def test_coin_is_required():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.describe_networks("")


def test_public_metadata_does_not_claim_transfer_verification():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "transfer_verification_available"
    ] is False

    for network in result["networks"]:
        assert network[
            "deposit_enabled"
        ] is None
        assert network[
            "withdraw_enabled"
        ] is None


def test_public_metadata_cannot_be_mistaken_for_network_info():
    from exchanges.network_registry import NetworkInfo

    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert networks

    assert all(
        not isinstance(
            network,
            NetworkInfo,
        )
        for network in networks
    )


def test_operational_status_does_not_imply_transfer_capability():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    trx = networks[0]

    assert trx["operational"] is True
    assert trx["deposit_enabled"] is None
    assert trx["withdraw_enabled"] is None


def test_closed_network_also_remains_transfer_unverified():
    adapter = PhemexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    ftm = networks[1]

    assert ftm["operational"] is False
    assert ftm["deposit_enabled"] is None
    assert ftm["withdraw_enabled"] is None
