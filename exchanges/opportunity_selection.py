"""
ArbOS™
EX-016
Opportunity Selection

Selects the single best executable arbitrage opportunity
using the ranking logic from EX-015.
"""

from exchanges.opportunity_ranking import OpportunityRanking


class OpportunitySelection:

    @staticmethod
    def select(opportunities):
        """
        Return the highest-ranked executable opportunity.

        Returns:
            dict: best executable opportunity
            None: if no executable opportunity exists

        The original input list is not modified.
        """

        ranked = OpportunityRanking.rank(opportunities)

        if not ranked:
            return None

        return ranked[0]
