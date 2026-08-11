from exchanges.public_native_source_candidate_selector import (
    PublicNativeSourceCandidateSelector,
)


def test_gate_prefers_spot_currency_pairs():
    candidates = [
        "publicFlashSwapGetCurrencyPairs",
        "publicMarginGetCurrencyPairs",
        "publicSpotGetCurrencyPairs",
        "publicSpotGetCurrencyPairsCurrencyPair",
    ]

    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="gate",
        candidate_methods=candidates,
    )

    assert result["selected_method"] == (
        "publicSpotGetCurrencyPairs"
    )
    assert result["candidate_selected"] is True


def test_bitget_prefers_spot_public_symbols():
    candidates = [
        "publicMixGetV2MixMarketContracts",
        "publicSpotGetV2SpotMarketFills",
        "publicSpotGetV2SpotPublicSymbols",
        "publicUtaGetV3MarketInstruments",
    ]

    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="bitget",
        candidate_methods=candidates,
    )

    assert result["selected_method"] == (
        "publicSpotGetV2SpotPublicSymbols"
    )


def test_xt_prefers_spot_symbol():
    candidates = [
        "publicLinearGetFutureMarketV1PublicSymbolList",
        "publicInverseGetFutureMarketV1PublicSymbolList",
        "publicSpotGetSymbol",
    ]

    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="xt",
        candidate_methods=candidates,
    )

    assert result["selected_method"] == (
        "publicSpotGetSymbol"
    )


def test_htx_prefers_common_symbols():
    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="htx",
        candidate_methods=[
            "publicGetCommonSymbols",
        ],
    )

    assert result["selected_method"] == (
        "publicGetCommonSymbols"
    )


def test_kucoin_prefers_symbols_over_markets():
    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="kucoin",
        candidate_methods=[
            "publicGetMarkets",
            "publicGetSymbols",
        ],
    )

    assert result["selected_method"] == (
        "publicGetSymbols"
    )


def test_digifinex_prefers_existing_native_candidate():
    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="digifinex",
        candidate_methods=[
            "publicSpotGetMarginSymbols",
            "publicSpotGetMarketSymbols",
            "publicSpotGetMarkets",
            "publicSpotGetSpotSymbols",
        ],
    )

    assert result["selected_method"] in {
        "publicSpotGetMarketSymbols",
        "publicSpotGetMarkets",
        "publicSpotGetSpotSymbols",
    }


def test_unknown_exchange_does_not_guess():
    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="unknown",
        candidate_methods=[
            "publicGetSomethingMarkets",
        ],
    )

    assert result["selected_method"] is None
    assert result["candidate_selected"] is False


def test_selector_does_not_execute_method():
    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="kucoin",
        candidate_methods=[
            "publicGetSymbols",
        ],
    )

    assert result["selection_complete"] is True
    assert result["public_api_called"] is False
    assert result["live_order_submitted"] is False


def test_returns_full_approved_method_chain():
    result = PublicNativeSourceCandidateSelector().select(
        exchange_id="digifinex",
        candidate_methods=[
            "publicSpotGetMarketSymbols",
            "publicSpotGetSpotSymbols",
            "publicSpotGetMarkets",
        ],
    )

    assert result["approved_methods"] == [
        "publicSpotGetMarketSymbols",
        "publicSpotGetSpotSymbols",
        "publicSpotGetMarkets",
    ]

    assert result["approved_method_count"] == 3
