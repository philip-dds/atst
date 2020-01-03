from sqlalchemy import Column, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.dialects.postgresql import UUID

from transitions import Machine
from transitions.extensions.states import add_state_features, Tags

from flask import current_app as app

from atst.database import db
from atst.queue import celery
from atst.models.types import Id
from atst.models.base import Base
import atst.models.mixins as mixins
from atst.models.mixins.state_machines import FSMStates


@add_state_features(Tags)
class StateMachineWithTags(Machine):
    pass

class PortfolioStateMachine(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin,
    mixins.AzureFSMMixin,
    mixins.TenantMixin,
    mixins.BillingProfileMixin,
):
    __tablename__ = "portfolio_state_machines"

    id = Id()

    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id"),
    )
    portfolio = relationship("Portfolio", back_populates="state_machine")

    state = Column(
        SQLAEnum(FSMStates, native_enum=False, create_constraint=False),
        default=FSMStates.UNSTARTED, nullable=False
    )

    def __init__(self, portfolio, csp=None, **kwargs):
        self.portfolio = portfolio
        self.attach_machine()

    def after_state_change(self, event):
        db.session.add(self)
        db.session.commit()

    @reconstructor
    def attach_machine(self):
        """ This is called as a result of a sqlalchemy query.  Attach a machine depending on the current state.
        """
        self.machine = StateMachineWithTags(
                model = self,
                send_event=True,
                initial=self.state.name if self.state else FSMStates.UNSTARTED.name,
                auto_transitions=False,
                after_state_change='after_state_change',
        )
        #TODO see if based on current state tag some of these states/transitions can be excluded
        #if self.machine.get_state(self.state).is_system
        #if self.machine.get_state(self.state).is_tenant_creation
        #if self.machine.get_state(self.state).is_billing_profile_creation

        states, transitions = self._azure_transitions()
        self.machine.add_states(self.states_base+states)
        self.machine.add_transitions(self.transitions_base+transitions)

    def trigger_next_transition(self, csp):
        state_obj = self.machine.get_state(self.state)
        if state_obj.is_system:
            if self.state == FSMStates.UNSTARTED:
                self.init()

            elif fsm.state == FSMStates.STARTING:
                self.start()

            elif self.state == FSMStates.STARTED:
                # iterate over stages and check the state tag
                #for stage in [st.name for st in list(AzureFSMStages)]:
                #self.machine.get_triggers(sm.state)
                #fsm.create_tenant(csp=csp.cloud)
                #getattr(self, 'create_tenant')()
                #event = self.machine.events['create_tenant']
                #event.name
                #event.transitions

                pass
        elif state_obj.is_IN_PROGRESS:
            pass
            #fsm.finish_create_tenant()

        elif state_obj.is_TENANT:
            pass
        elif state_obj.is_BILLING_PROFILE:
            pass

    @property
    def application_id(self):
        return None
