from app.risk.manager import RiskManager
from app.config import settings

def test_risk_manager_initial_equity():
    rm = RiskManager()
    rm.set_initial_equity(10000.0)
    assert rm.initial_equity == 10000.0

def test_can_trade_success():
    rm = RiskManager()
    rm.set_initial_equity(10000.0)

    # Loss = 0
    account = {'equity': 10000.0}
    assert rm.can_trade(account) is True

    # Loss = 50 (within limit 100)
    account = {'equity': 9950.0}
    assert rm.can_trade(account) is True

def test_can_trade_failure():
    rm = RiskManager()
    rm.set_initial_equity(10000.0)

    # Loss = 200 (limit 100)
    account = {'equity': 9800.0}
    assert rm.can_trade(account) is False

def test_validate_order_success():
    rm = RiskManager()
    # Account has 5000 BP
    account = {'buying_power': 5000.0}

    # Order cost = 100 * 10 = 1000. BP=5000. OK.
    # Max Pos Size = 1000. OK.
    # Note: price * qty <= max_pos_size
    assert rm.validate_order("TEST", 100, 10.0, account) is True

def test_validate_order_insufficient_bp():
    rm = RiskManager()
    account = {'buying_power': 500.0}

    # Cost = 1000. > 500. Fail.
    assert rm.validate_order("TEST", 100, 10.0, account) is False

def test_validate_order_max_pos_size():
    rm = RiskManager()
    account = {'buying_power': 5000.0}

    # Cost = 2000. > Max Pos Size (1000). Fail.
    assert rm.validate_order("TEST", 200, 10.0, account) is False
