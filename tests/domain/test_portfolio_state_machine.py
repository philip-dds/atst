import pytest

from tests.factories import (
    PortfolioFactory,
    PortfolioStateMachineFactory,
)

from atst.models import FSMStates


@pytest.fixture(scope="function")
def portfolio():
    portfolio = PortfolioFactory.create()
    return portfolio

def test_fsm_creation(portfolio):
    sm = PortfolioStateMachineFactory.create(portfolio=portfolio)
    assert sm.portfolio

def test_fsm_transition_start(portfolio):
    sm = PortfolioStateMachineFactory.create(portfolio=portfolio)
    assert sm.portfolio
    sm.start()
    assert sm.state == FSMStates.STARTED


