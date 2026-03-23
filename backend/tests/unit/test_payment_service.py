"""Tests for mock payment gateway — intent, confirm, refund."""
from decimal import Decimal


def test_mock_gateway_id_format():
    from app.services.payment_service import _mock_gateway_id
    gid = _mock_gateway_id()
    assert gid.startswith("pi_")
    assert len(gid) > 20


# Note: Full payment tests require async DB session — integration tests.
# These test the pure functions.
