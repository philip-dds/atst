from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, text, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


from atst.queue import celery
from transitions import Machine

from flask import current_app as app

from atst.models.types import Id
from atst.models.base import Base
from atst.domain.csp import MockCSP, AzureCSP
import atst.models.mixins as mixins
from atst.database import db


@celery.task(bind=True)
def create_tenant():
    print('celery worker creating tenant')


class FSMStates(Enum):
    UNSTARTED = "unstarted"
    STARTING = "starting"
    STARTED = "started"
    TENANT_CREATED = "tenant created"
    ATAT_PRINCPAL_CREATED = "atat principal created"
    AAP_ACCESS_GRANTED = "AAP access granted"
    AAP_ACCESS_CONSENT_COMPLETED = "consent AAP access"
    TENANT_ADMIN_PW_UPDATE_FORKED = "fork tenant admin pw update"
    BILLING_ADMIN_CREATED = "billing admin created"
    BILLING_PROFILE_CREATED = "billing profile created"
    PAYMENT_OBJECT_CREATED = "payment objects created"
    BILLING_ALERTS_REGISTERED = "billing alerts registered" # order may change
    ROOT_MGMT_GROUP_CREATED = "root mgmt group created" # long running or poll url
    AAD_DOMAIN_PURCHASED = "AAD domain purchased" # long running or poll url
    POLICY_DEF_LIBRARY_CREATED = "policy def library created" # order may change
    ROOT_MGMT_GROUP_POLICIES_APPLIED = "root mgmt group policies applied"
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
            "trigger": "init",
            "source": FSMStates.UNSTARTED,
            "dest": FSMStates.STARTING,
            #"conditions": "can_start",
        },
        {
            "trigger": "start",
            "source": FSMStates.STARTING,
            "dest": FSMStates.STARTED,
            #"conditions": "can_start",
        },
        #{
        #    "trigger": "create_tenant",
        #    "source": FSMStates.STARTED,
        #    "dest": FSMStates.TENANT_CREATED,
        ##    "after": "csp_create_tenant",
            #"conditions": "is_tenant_created",
        #},
        #{
        #    "trigger": "complete",
        #    "source": FSMStates.STARTED,
        #    "dest": FSMStates.COMPLETED,
        ##    "conditions": "can_complete",
        #},
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
        #FSMStatesPrefix
        #csp specific states
        #FSMStatesSuffix
        Machine.__init__(self,
                states=FSMStates,
                transitions=PortfolioStateMachine.transitions,
                send_event=True,
                initial=self.state.value if self.state else FSMStates.UNSTARTED,
        )
        #self.add_ordered_transitions()

        self.add_transition("start",
                FSMStates.STARTING,
                FSMStates.STARTED,
                prepare="prepare_start",
                before="before_start",
                after="after_start",
        )

        self.add_transition("create_tenant",
                FSMStates.STARTED,
                FSMStates.TENANT_CREATED,
                prepare="prepare_create_tenant",
                before="before_create_tenant",
                after="after_create_tenant",
        )
        self.add_transition("fail", "*", FSMStates.FAILED)

    @property
    def application_id(self):
        return None

    #def next_state():
    #    pass
        #self.csp.cloud.create_tenant()

    def prepare_create_tenant(self, event):
        #self.csp.cloud.create_tenant()
        print('prepare tenant.')
        print(event.kwargs)
        print(self.state)

    def before_create_tenant(self, event):
        #self.csp.cloud.create_tenant()
        print('before tenant.')
        print(event.kwargs)
        print(self.state)

        create_tenant.delay()

    def after_create_tenant(self, event):
        #self.csp.cloud.create_tenant()
        print('after state transitions to TENANT_CREATED.')
        print(event.kwargs)
        print(self.state)


    def can_start(self):
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
