from exchanges.execution_failure_recovery import ExecutionFailureRecovery
    

def test_create_recovery_engine():  
    
        engine = ExecutionFailureRecovery()
    
        assert engine is not None
    
    
def test_register_failure():
    
        engine = ExecutionFailureRecovery()
    
        result = engine.register_failure(
            "tx-001",
            "network_timeout"
        )
    
        assert result["transaction_id"] == "tx-001"
    
    
def test_failure_status_created():
    
        engine = ExecutionFailureRecovery()
    
        result = engine.register_failure(
            "tx-001",
            "network_timeout"
        )
    
        assert result["status"] == "RECOVERY_PENDING"
    
    
def test_process_recovery():
    
        engine = ExecutionFailureRecovery()
    
        engine.register_failure(
            "tx-001",
            "network_timeout"
        )
    
        result = engine.process_recovery(
            "tx-001"
        )
    
        assert result["status"] == "RECOVERED"
    
    
def test_failed_recovery():
    
        engine = ExecutionFailureRecovery()
    
        result = engine.process_recovery(
            "missing"
        )
    
        assert result["success"] is False
    
    
def test_duplicate_recovery_blocked():
    
        engine = ExecutionFailureRecovery()
    
        engine.register_failure(
            "tx-001",
            "network_timeout"
        )
    
        engine.process_recovery(
            "tx-001"
        )
    
        result = engine.process_recovery(
            "tx-001"
        )
    
        assert result["success"] is False


def test_recovery_history():
    
        engine = ExecutionFailureRecovery()
    
        engine.register_failure(
            "tx-001",
            "network_timeout"
        )
    
        history = engine.get_history()
    
        assert len(history) == 1
    

def test_failure_reason_saved():
    
        engine = ExecutionFailureRecovery()
    
        result = engine.register_failure(
            "tx-001",
            "exchange_error"
        )
    
        assert result["reason"] == "exchange_error"
