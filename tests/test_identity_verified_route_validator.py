from exchanges.route_validator import (
    RouteValidator,
)


def test_verified_chain_identity_is_executable():
    result = (
        RouteValidator
        .validate_identity_verified_transfer_route(
            source_exchange="kucoin",
            destination_exchange="gate",
            coin="USDT",
            source_network_records=[
                {
                    "network": "TRC20",
                    "chain_id": "tron",
                    "withdraw": True,
                    "withdraw_fee": 1.0,
                },
            ],
            destination_network_records=[
                {
                    "network": "TRC20",
                    "chain_id": "tron",
                    "deposit": True,
                },
            ],
        )
    )

    assert result.executable is True
    assert result.network == "TRC20"
    assert result.withdraw_fee == 1.0


def test_unverified_same_name_network_is_blocked():
    result = (
        RouteValidator
        .validate_identity_verified_transfer_route(
            source_exchange="kucoin",
            destination_exchange="digifinex",
            coin="COTI",
            source_network_records=[
                {
                    "network": "COTI",
                    "chain_id": "cotievm",
                    "withdraw": True,
                    "withdraw_fee": 150.0,
                },
            ],
            destination_network_records=[
                {
                    "network": "COTI",
                    "chain_id": "",
                    "deposit": True,
                },
            ],
        )
    )

    assert result.executable is False
    assert result.network is None


def test_conflicting_chain_ids_are_blocked():
    result = (
        RouteValidator
        .validate_identity_verified_transfer_route(
            source_exchange="a",
            destination_exchange="b",
            coin="TOKEN",
            source_network_records=[
                {
                    "network": "MAINNET",
                    "chain_id": "chain-a",
                    "withdraw": True,
                    "withdraw_fee": 1.0,
                },
            ],
            destination_network_records=[
                {
                    "network": "MAINNET",
                    "chain_id": "chain-b",
                    "deposit": True,
                },
            ],
        )
    )

    assert result.executable is False


def test_matching_contract_identity_is_executable():
    result = (
        RouteValidator
        .validate_identity_verified_transfer_route(
            source_exchange="a",
            destination_exchange="b",
            coin="TOKEN",
            source_network_records=[
                {
                    "network": "ERC20",
                    "contract_address": "0xABC123",
                    "withdraw": True,
                    "withdraw_fee": 3.0,
                },
            ],
            destination_network_records=[
                {
                    "network": "ERC20",
                    "contract_address": "0xabc123",
                    "deposit": True,
                },
            ],
        )
    )

    assert result.executable is True
    assert result.network == "ERC20"


def test_strict_validator_selects_lowest_fee_verified_network():
    result = (
        RouteValidator
        .validate_identity_verified_transfer_route(
            source_exchange="a",
            destination_exchange="b",
            coin="USDT",
            source_network_records=[
                {
                    "network": "ERC20",
                    "chain_id": "ethereum",
                    "withdraw": True,
                    "withdraw_fee": 8.0,
                },
                {
                    "network": "TRC20",
                    "chain_id": "tron",
                    "withdraw": True,
                    "withdraw_fee": 1.0,
                },
            ],
            destination_network_records=[
                {
                    "network": "ERC20",
                    "chain_id": "ethereum",
                    "deposit": True,
                },
                {
                    "network": "TRC20",
                    "chain_id": "tron",
                    "deposit": True,
                },
            ],
        )
    )

    assert result.executable is True
    assert result.network == "TRC20"
    assert result.withdraw_fee == 1.0


def test_unknown_withdraw_fee_is_not_executable():
    result = (
        RouteValidator
        .validate_identity_verified_transfer_route(
            source_exchange="a",
            destination_exchange="b",
            coin="USDT",
            source_network_records=[
                {
                    "network": "TRC20",
                    "chain_id": "tron",
                    "withdraw": True,
                    "withdraw_fee": None,
                },
            ],
            destination_network_records=[
                {
                    "network": "TRC20",
                    "chain_id": "tron",
                    "deposit": True,
                },
            ],
        )
    )

    assert result.executable is False


def test_legacy_route_validator_remains_available():
    from exchanges.network_registry import (
        NetworkInfo,
    )

    result = RouteValidator.validate_transfer_route(
        [
            NetworkInfo(
                "USDT",
                "TRC20",
                withdraw_fee=1.0,
            ),
        ],
        [
            NetworkInfo(
                "USDT",
                "TRC20",
            ),
        ],
    )

    assert result.executable is True
    assert result.network == "TRC20"
