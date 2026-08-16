"""
ArbOS™
EX-232
Phemex Spot Scale Resolver

Resolves market-specific Phemex spot price and quantity scales
from the public products catalogue.

Important:
- only Spot products are considered
- perpetual products are ignored
- price scale comes from the spot product
- quantity scale comes from the base currency valueScale

Read-only.
No authentication.
No transfers.
No live orders.
"""


class PhemexSpotScaleResolver:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    @staticmethod
    def _normalize_symbol(
        symbol,
    ):
        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        compact = symbol.replace(
            "/",
            "",
        )

        if compact.startswith("S"):
            compact = compact[1:]

        return (
            "s"
            + compact
        )

    def resolve(
        self,
        symbol,
    ):
        native_symbol = (
            self._normalize_symbol(
                symbol
            )
        )

        try:
            payload = (
                self._client
                .fetch_products()
            )
        except Exception as exc:
            raise RuntimeError(
                "Phemex spot scale unavailable: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Phemex spot scale unavailable: "
                "invalid response"
            )

        if payload.get("code") != 0:
            raise RuntimeError(
                "Phemex spot scale unavailable: "
                "catalogue unavailable"
            )

        data = payload.get(
            "data"
        )

        if not isinstance(
            data,
            dict,
        ):
            raise RuntimeError(
                "Phemex spot scale unavailable: "
                "invalid catalogue"
            )

        products = data.get(
            "products"
        )

        currencies = data.get(
            "currencies"
        )

        if (
            not isinstance(
                products,
                list,
            )
            or not isinstance(
                currencies,
                list,
            )
        ):
            raise RuntimeError(
                "Phemex spot scale unavailable: "
                "missing catalogue metadata"
            )

        spot_product = None

        for product in products:
            if not isinstance(
                product,
                dict,
            ):
                continue

            if (
                str(
                    product.get(
                        "type",
                        "",
                    )
                ).strip()
                != "Spot"
            ):
                continue

            product_symbol = str(
                product.get(
                    "symbol",
                    "",
                )
                or ""
            ).strip()

            if (
                product_symbol
                == native_symbol
            ):
                spot_product = product
                break

        if spot_product is None:
            raise RuntimeError(
                "Phemex spot scale unavailable: "
                "spot product not found"
            )

        base_currency = str(
            spot_product.get(
                "baseCurrency",
                "",
            )
            or ""
        ).strip().upper()

        price_scale = (
            spot_product.get(
                "priceScale"
            )
        )

        if (
            not base_currency
            or not isinstance(
                price_scale,
                int,
            )
            or isinstance(
                price_scale,
                bool,
            )
            or price_scale < 0
        ):
            raise RuntimeError(
                "Phemex spot scale unavailable: "
                "invalid spot product metadata"
            )

        quantity_scale = None

        for currency in currencies:
            if not isinstance(
                currency,
                dict,
            ):
                continue

            currency_name = str(
                currency.get(
                    "currency",
                    "",
                )
                or ""
            ).strip().upper()

            if (
                currency_name
                != base_currency
            ):
                continue

            value_scale = (
                currency.get(
                    "valueScale"
                )
            )

            if (
                isinstance(
                    value_scale,
                    int,
                )
                and not isinstance(
                    value_scale,
                    bool,
                )
                and value_scale >= 0
            ):
                quantity_scale = (
                    value_scale
                )

            break

        if quantity_scale is None:
            raise RuntimeError(
                "Phemex spot scale unavailable: "
                "base currency scale not found"
            )

        return {
            "native_symbol": native_symbol,
            "price_scale": price_scale,
            "quantity_scale": quantity_scale,
        }
