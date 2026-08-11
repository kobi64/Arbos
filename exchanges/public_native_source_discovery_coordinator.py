"""
ArbOS™
EX-188
Public Native Source Discovery Coordinator

Composes:
- public native capability discovery
- exchange-specific safe candidate selection
- one selected public catalogue probe

Public market-data discovery only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.public_native_source_discoverer import (
    PublicNativeSourceDiscoverer,
)
from exchanges.public_native_source_candidate_selector import (
    PublicNativeSourceCandidateSelector,
)
from exchanges.public_native_source_probe_chain import (
    PublicNativeSourceProbeChain,
)


class PublicNativeSourceDiscoveryCoordinator:
    def run(
        self,
        exchange,
    ):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        discovery = (
            PublicNativeSourceDiscoverer()
            .discover(exchange)
        )

        selection = (
            PublicNativeSourceCandidateSelector()
            .select(
                exchange_id=discovery[
                    "exchange_id"
                ],
                candidate_methods=discovery[
                    "candidate_methods"
                ],
            )
        )

        selected_method = selection.get(
            "selected_method"
        )

        if selected_method is None:
            return {
                **discovery,
                **selection,
                "probe_success": False,
                "response_type": None,
                "response": None,
                "error_type": (
                    "NoCandidateSelected"
                ),
                "error": (
                    "no approved public spot "
                    "catalogue method selected"
                ),
                "public_api_called": False,
                "live_order_submitted": False,
            }

        probe = (
            PublicNativeSourceProbeChain()
            .probe(
                exchange=exchange,
                method_names=selection.get(
                    "approved_methods",
                    [],
                ),
            )
        )

        return {
            **discovery,
            **selection,
            **probe,
            "selected_method": (
                probe.get(
                    "successful_method"
                )
                or selected_method
            ),
            "live_order_submitted": False,
        }
