from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, text, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from transitions import Machine

from flask import current_app as app

from atst.models.types import Id
from atst.models.base import Base
from atst.domain.csp import MockCSP, AzureCSP
import atst.models.mixins as mixins
from atst.database import db


class FSMStates(Enum):
    UNSTARTED = "unstarted"
    STARTING = "starting"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class PortfolioStateMachine(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin, Machine
):
    __tablename__ = "portfolio_state_machines"

    id = Id()

    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id"),
    )
    portfolio = relationship("Portfolio", back_populates="state_machine")

    state = Column(
        SQLAEnum(FSMStates, native_enum=False), default=FSMStates.UNSTARTED, nullable=True
    )

    # can use on_exit as the callback to serialize fetched/updated data as well as the current
    # state that workers should resume on
    #states = [
    #    {
    #        "name": FSMStates.UNSTARTED,
    #        "on_exit": FSMStates.STARTING
    #    },
    #    FSMStates.STARTED,
    #    FSMStates.COMPLETED,
    #]
    transitions = [
        {
            "trigger": "start",
            "source": FSMStates.UNSTARTED,
            "dest": FSMStates.STARTED,
            "conditions": "can_start",
        },
        {
            "trigger": "complete",
            "source": FSMStates.STARTED,
            "dest": FSMStates.COMPLETED,
            "conditions": "can_complete",
        },
        {
            "trigger": "reset",
            "source": FSMStates.COMPLETED,
            "dest": FSMStates.UNSTARTED,
            "conditions": "can_restart",
        },
    ]

    def __init__(self, portfolio, source=None, csp=None, **kwargs):
        if source is not None:
            pass  # hydrate from source

        if csp is not None:
            self.csp = AzureCSP().cloud
        else:
            self.csp = MockCSP(app).cloud

        self.portfolio = portfolio
        Machine.__init__(self,
                states=FSMStates,
                transitions=PortfolioStateMachine.transitions,
                initial=self.state.value if self.state else FSMStates.UNSTARTED,
        )

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
