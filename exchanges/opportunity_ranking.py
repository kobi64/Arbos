"""
ArbOS™
EX-015
Opportunity Ranking

Ranks executable arbitrage opportunities by profit percentage,
using net profit as a secondary tie-breaker.
"""

import math


class OpportunityRanking:

    @staticmethod
    def _ranking_value(opportunity, field):
        if field not in opportunity:
            raise ValueError(f"{field} is required")

        value = opportunity[field]

        if isinstance(value, bool):
            raise ValueError(
                f"{field} must be a finite number"
            )

        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{field} must be a finite number"
            )

        if not math.isfinite(value):
            raise ValueError(
                f"{field} must be a finite number"
            )

        return value

    @classmethod
    def rank(cls, opportunities):
        """
        Return executable opportunities ranked from best to worst.

        Primary ranking:
            profit_percent descending

        Tie-breaker:
            net_profit descending

        Executable opportunities must provide finite numeric
        profit_percent and net_profit values.

        The original input list and opportunity mappings are not
        modified.
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
                cls._ranking_value(
                    opportunity,
                    "profit_percent",
                ),
                cls._ranking_value(
                    opportunity,
                    "net_profit",
                ),
            ),
            reverse=True,
        )
