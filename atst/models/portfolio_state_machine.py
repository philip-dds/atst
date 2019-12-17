from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, text, Enum as SQLAEnum
from sqlalchemy.types import PickleType
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from atst.models.types import Id
from atst.models.base import Base
from atst.domain.csp import MockCSP, AzureCSP
import atst.models.mixins as mixins
from atst.database import db


class FSMState(Enum):
    UNSTARTED = "unstarted"
    STARTING = "starting"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class PortfolioStateMachine(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin
):
    __tablename__ = "portfolio_state_machines"

    id = Id()

    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id"),
        #server_default=text("uuid_generate_v4()"),
    )
    portfolio = relationship("Portfolio", back_populates="state_machine")

    machine_instance = Column(PickleType)

    state = Column(
        SQLAEnum(FSMState, native_enum=False), default=FSMState.UNSTARTED, nullable=True
    )

    # can use on_exit as the callback to serialize fetched/updated data as well as the current
    # state that workers should resume on
    states = [
        {"name": FSMState.UNSTARTED, "on_exit": FSMState.STARTING},
        "started",
        "completed"
    ]
    transitions = [
        {
            "trigger": "start",
            "source": FSMState.UNSTARTED,
            "dest": FSMState.STARTED,
            "conditions": "can_start",
        },
        {
            "trigger": "complete",
            "source": FSMState.STARTED,
            "dest": FSMState.COMPLETED,
            "conditions": "can_complete",
        },
        {
            "trigger": "reset",
            "source": FSMState.COMPLETED,
            "dest": FSMState.UNSTARTED,
            "conditions": "can_restart",
        },
    ]

    #def __init__(self, source=None, csp=None):
    #    if source is not None:
    #        pass  # hydrate from source

        #if csp is not None:
        #    self.csp = AzureCSP().cloud
        #else:
        #    self.csp = MockCSP().cloud

        #self.machine = transitions.Machine(
        #    model=self,
        #    initial=self.current_state,
        #    states=PortfolioFSM.states,
        #    ordered_transitions=PortfolioFSM.transitions,
        #)

    @property
    def application_id(self):
        return None

    #def next_state():
    #    pass
        #self.csp.cloud.create_tenant()

    def can_start(self):
        #import ipdb
        #ipdb.set_trace()
        #self.force_complete()
        return True

    def can_restart(self):
        return True

    def can_complete(self):
        #import ipdb
        #ipdb.set_trace()
        return False

    def can_force_complete(self):
        #import ipdb
        #ipdb.set_trace()
        return True

    def starting(self):
        #self.current_state = self.state
        #import ipdb
        #ipdb.set_trace()
        return True
