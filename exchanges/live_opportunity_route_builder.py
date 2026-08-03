"""
ArbOS™
EX-077
Live Opportunity Route Builder
"""


class LiveOpportunityRouteBuilder:
    def build(self, opportunity):
        if opportunity is None:
            raise ValueError("opportunity is required")

        opportunity_id = opportunity.get("opportunity_id")
        if not opportunity_id:
            raise ValueError("opportunity_id is required")

        legs = opportunity.get("legs")
        if not legs:
            raise ValueError("legs are required")

        built_legs = []

        for leg in legs:
            symbol = leg.get("symbol")
            if not symbol:
                raise ValueError("leg symbol is required")

            built_legs.append(dict(leg))

        return {
            "route_id": str(opportunity_id),
            "legs": built_legs,
        }
