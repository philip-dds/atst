from transitions import Machine
from atst.database import db

from atst.models import FSMStates, PortfolioStateMachine

from .query import PortfoliosQuery, PortfolioStateMachinesQuery


class PortfolioStateMachines(object):
    @classmethod
    def create(cls, portfolio, **sm_attrs):
        sm_attrs.update({'portfolio': portfolio})
        sm = PortfolioStateMachinesQuery.create(**sm_attrs)
        machine = sm.machine_instance = Machine(
            model = sm,
            states = FSMStates, #[st.value for st in FSMStates],
            initial = FSMStates.UNSTARTED,
            #ordered_transitions= sm.__class__.transitions,
        )
        machine.add_ordered_transitions()
        PortfolioStateMachinesQuery.add_and_commit(sm)
        return sm

    #@classmethod
    #def get(cls, portfolio_id):
        #sm = PortfolioStateMachinesQuery.get(portfolio_id)
    #    sm = db.session.query(PortfolioStateMachine).filter_by(portfolio_id=portfolio_id).one()
    #    machine = sm.machine = Machine(
    #        model = sm,
    #        states = FSMStates, #[st.value for st in FSMStates],
    #        initial = FSMStates.UNSTARTED,
            #ordered_transitions= sm.__class__.transitions,
    #    )
    #    machine.add_ordered_transitions()
    #    return sm
