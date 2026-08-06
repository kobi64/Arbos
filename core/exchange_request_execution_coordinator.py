"""
ArbOS™
EX-112
Exchange Request Execution Coordinator
"""


class ExchangeRequestExecutionCoordinator:
    def __init__(
        self,
        queue_manager,
        rate_limiter,
        connectivity_supervisor,
        circuit_breaker,
        dispatcher,
    ):
        self._queue = queue_manager
        self._rate_limiter = rate_limiter
        self._connectivity = connectivity_supervisor
        self._circuit_breaker = circuit_breaker
        self._dispatcher = dispatcher

    def process_next(self):
        request = self._queue.dequeue()

        if request is None:
            return None

        exchange_id = request.get("exchange_id")

        connectivity = self._connectivity.check_health(exchange_id)

        if not connectivity["healthy"]:
            self._queue.enqueue(request)
            return {
                "processed": False,
                "success": False,
                "request_id": request["request_id"],
                "reason": connectivity["reason"],
            }

        circuit = self._circuit_breaker.allow_execution()

        if not circuit["allowed"]:
            self._queue.enqueue(request)
            return {
                "processed": False,
                "success": False,
                "request_id": request["request_id"],
                "reason": circuit["reason"],
            }

        rate = self._rate_limiter.allow_request(exchange_id)

        if not rate["allowed"]:
            self._queue.enqueue(request)
            return {
                "processed": False,
                "success": False,
                "request_id": request["request_id"],
                "reason": rate["reason"],
            }

        result = self._dispatcher.execute(request)

        if result.get("success"):
            self._circuit_breaker.record_success()
        else:
            self._circuit_breaker.record_failure(
                result.get("reason", "dispatch_failed")
            )

        return {
            "processed": True,
            "success": bool(result.get("success")),
            "request_id": request["request_id"],
            "result": result,
        }
