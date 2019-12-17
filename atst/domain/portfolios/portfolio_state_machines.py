from transitions import Machine
from atst.database import db

from atst.models import FSMState


from .query import PortfoliosQuery,PortfolioStateMachineQuery


class PortfolioStateMachines(object):
    @classmethod
    def create(cls, portfolio, **sm_attrs):
        sm_attrs.update({'portfolio': portfolio})
        sm = PortfolioStateMachineQuery.create(**sm_attrs)
        machine = sm.machine_instance = Machine(
            model = sm,
            states = sm.__class__.states,
            initial = FSMState.UNSTARTED,
            ordered_transitions= sm.__class__.transitions,
        )
        PortfolioStateMachineQuery.add_and_commit(sm)
        return sm

    @classmethod
    def get(cls, portfolio_id):
        sm = PortfolioStateMachineQuery.get(portfolio_id)
        return sm
