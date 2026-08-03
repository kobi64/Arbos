"""
ArbOS™
EX-055
Order Reconciliation & State Recovery Engine
"""


class OrderReconciliationStateRecovery:
    def reconcile(self, local, remote):
        if local is None and remote is None:
            return {
                "state": "NO_ORDER",
                "recovery_required": False,
                "recovery_action": None,
            }

        if local is None:
            return {
                "state": "LOCAL_MISSING",
                "recovery_required": True,
                "recovery_action": "IMPORT_REMOTE_ORDER",
                "resolved_status": remote.get("status"),
                "resolved_filled": remote.get("filled", 0.0),
            }

        if remote is None:
            return {
                "state": "REMOTE_MISSING",
                "recovery_required": True,
                "recovery_action": "VERIFY_WITH_EXCHANGE",
                "resolved_status": local.get("status"),
                "resolved_filled": local.get("filled", 0.0),
            }

        if local.get("order_id") != remote.get("order_id"):
            raise ValueError("order IDs do not match")

        local_status = local.get("status")
        remote_status = remote.get("status")

        local_filled = float(local.get("filled", 0.0))
        remote_filled = float(remote.get("filled", 0.0))

        if (
            local_status == remote_status
            and local_filled == remote_filled
        ):
            return {
                "state": "MATCHED",
                "recovery_required": False,
                "recovery_action": None,
                "resolved_status": remote_status,
                "resolved_filled": remote_filled,
            }

        if local_status != remote_status:
            return {
                "state": "REMOTE_STATE_CHANGED",
                "recovery_required": True,
                "recovery_action": "SYNC_FROM_EXCHANGE",
                "resolved_status": remote_status,
                "resolved_filled": remote_filled,
            }

        if local_filled != remote_filled:
            return {
                "state": "FILL_MISMATCH",
                "recovery_required": True,
                "recovery_action": "SYNC_FROM_EXCHANGE",
                "resolved_status": remote_status,
                "resolved_filled": remote_filled,
            }

        return {
            "state": "MATCHED",
            "recovery_required": False,
            "recovery_action": None,
            "resolved_status": remote_status,
            "resolved_filled": remote_filled,
        }
