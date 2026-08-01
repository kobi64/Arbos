"""
ArbOS™
EX-015
Opportunity Ranking

Ranks executable arbitrage opportunities by profit percentage,
using net profit as a secondary tie-breaker.
"""


class OpportunityRanking:

    @staticmethod
    def rank(opportunities):
        """
        Return executable opportunities ranked from best to worst.

        Primary ranking:
            profit_percent descending

        Tie-breaker:
            net_profit descending

        The original input list is not modified.
        """

        if not opportunities:
            return []

        executable = [
            opportunity
            for opportunity in opportunities
            if opportunity.get("executable") is True
        ]

        return sorted(
            executable,
            key=lambda opportunity: (
                opportunity.get("profit_percent", 0.0),
                opportunity.get("net_profit", 0.0),
            ),
            reverse=True,
        )
