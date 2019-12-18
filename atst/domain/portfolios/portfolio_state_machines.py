from transitions import Machine
from atst.database import db

from atst.models import FSMStates, PortfolioStateMachine

from .query import PortfoliosQuery, PortfolioStateMachinesQuery


class PortfolioStateMachines(object):
    @classmethod
    def create(cls, portfolio, **sm_attrs):
        sm_attrs.update({'portfolio': portfolio})
        sm = PortfolioStateMachinesQuery.create(**sm_attrs)
        return sm
