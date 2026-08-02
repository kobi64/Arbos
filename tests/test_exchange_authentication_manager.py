from exchanges.exchange_authentication_manager import ExchangeAuthenticationManager


def test_create_auth_manager():

    manager = ExchangeAuthenticationManager()

    assert manager is not None


def test_add_credentials():

    manager = ExchangeAuthenticationManager()

    result = manager.add_credentials(
        "HTX",
        "api-key",
        "secret"
    )

    assert result["success"] is True


def test_validate_credentials():

    manager = ExchangeAuthenticationManager()

    manager.add_credentials(
        "HTX",
        "api-key",
        "secret"
    )

    result = manager.validate("HTX")

    assert result is True


def test_missing_exchange():

    manager = ExchangeAuthenticationManager()

    result = manager.validate("UNKNOWN")

    assert result is False


def test_remove_credentials():

    manager = ExchangeAuthenticationManager()

    manager.add_credentials(
        "HTX",
        "api-key",
        "secret"
    )

    result = manager.remove_credentials("HTX")

    assert result["success"] is True


def test_auth_context():

    manager = ExchangeAuthenticationManager()

    manager.add_credentials(
        "HTX",
        "api-key",
        "secret"
    )

    result = manager.get_context("HTX")

    assert result["exchange"] == "HTX"


def test_invalid_credentials():

    manager = ExchangeAuthenticationManager()

    result = manager.add_credentials(
        "HTX",
        "",
        ""
    )

    assert result["success"] is False


def test_supported_exchange_list():

    manager = ExchangeAuthenticationManager()

    exchanges = manager.supported_exchanges()

    assert isinstance(exchanges, list)
