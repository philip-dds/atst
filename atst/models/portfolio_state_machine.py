from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, text, Enum as SQLAEnum
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.dialects.postgresql import UUID


from transitions import Machine

from flask import current_app as app

from atst.queue import celery
from atst.models.types import Id
from atst.models.base import Base
from atst.domain.csp import MockCSP, AzureCSP
from atst.domain.csp.cloud import ConnectionException, UnknownServerException
import atst.models.mixins as mixins
from atst.database import db



class FSMStates(Enum):
    UNSTARTED = "unstarted"
    STARTING = "starting"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    TENANT_CREATED = "tenant created"
    TENANT_CREATION_IN_PROGRESS = "tenant creation in progress"
    TENANT_CREATION_FAILED = "tenant creation failed"


class AzureFSMMixin():

    def prepare_init(self, event): pass
    def before_init(self, event): pass
    def after_init(self, event): pass

    def prepare_start(self, event): pass
    def before_start(self, event): pass
    def after_start(self, event): pass

    def prepare_reset(self, event): pass
    def before_reset(self, event): pass
    def after_reset(self, event): pass

    def prepare_create_tenant(self, event): pass
    def before_create_tenant(self, event): pass

    def after_create_tenant(self, event):
        # enter in_progress state and make api call
        # after state transitions to TENANT_CREATION_IN_PROGRESS.
        kwargs = dict(creds={"username": "mock-cloud", "pass": "shh"},
                    user_id='123',
                    password='123',
                    domain_name='123',
                    first_name='john',
                    last_name='doe',
                    country_code='US',
                    password_recovery_email_address='password@email.com')

        csp = event.kwargs.get('csp')

        if csp is not None:
            self.csp = AzureCSP(app).cloud
        else:
            self.csp = MockCSP(app).cloud

        for attempt in range(5):
            try:
                response = self.csp.create_tenant(**kwargs)
            except (ConnectionException, UnknownServerException) as exc:
                print('caught exception. retry', attempt)
                continue
            else: break
        else:
            # failed all attempts
            self.machine.fail_create_tenant()

        print(response)
        #{'tenant_id': 'string', 'user_id': 'string', 'user_object_id': 'string'}
        if self.portfolio.csp_data is None:
           self.portfolio.csp_data = {}
        self.portfolio.csp_data["tenant_data"] = response
        db.session.add(self.portfolio)
        db.session.commit()

    def is_tenant_created(self, event):
        # check portfolio csp details json field for fields

        print("is_tenant_created: ", self.portfolio.csp_data)
        if self.portfolio.csp_data is None or \
                not isinstance(self.portfolio.csp_data, dict):
            return False

        return all([
            "tenant_data" in self.portfolio.csp_data,
            "tenant_id" in self.portfolio.csp_data['tenant_data'],
            "user_id" in self.portfolio.csp_data['tenant_data'],
            "user_object_id" in self.portfolio.csp_data['tenant_data'],
        ])


class PortfolioStateMachine(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin, AzureFSMMixin
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
        print('PortfolioStateMachine.__init__')
        self.portfolio = portfolio
        self.init_machine()

    def after_state_change(self, event):
        db.session.add(self)
        db.session.commit()

    @reconstructor
    def init_machine(self):

        self.machine = Machine(
                model = self,
                states=FSMStates,
                send_event=True,
                initial=self.state.name if self.state else FSMStates.UNSTARTED.name,
                auto_transitions=False,
                after_state_change='after_state_change',
        )
        self.machine.add_transition(trigger="init", source=FSMStates.UNSTARTED, dest=FSMStates.STARTING,
                prepare="prepare_init", before="before_init", after="after_init",
        )
        self.machine.add_transition(trigger="start", source=FSMStates.STARTING, dest=FSMStates.STARTED,
                prepare="prepare_start", before="before_start", after="after_start",
        )
        self.machine.add_transition(trigger="reset", source="*", dest=FSMStates.UNSTARTED,
                prepare="prepare_reset", before="before_reset", after="after_reset",
        )
        self.machine.add_transition(trigger="fail", source="*", dest=FSMStates.FAILED)

        self.machine.add_transition("create_tenant",
                FSMStates.STARTED,
                FSMStates.TENANT_CREATION_IN_PROGRESS,
                prepare="prepare_create_tenant",
                before="before_create_tenant",
                after="after_create_tenant",
        )
        self.machine.add_transition("finish_create_tenant",
                FSMStates.TENANT_CREATION_IN_PROGRESS,
                FSMStates.TENANT_CREATED,
                conditions=["is_tenant_created",],
        )
        self.machine.add_transition("fail_create_tenant",
                FSMStates.TENANT_CREATION_IN_PROGRESS,
                FSMStates.TENANT_CREATION_FAILED,
        )


    @property
    def application_id(self):
        return None
