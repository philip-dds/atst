from dataclasses import dataclass
from typing import Dict#, Any

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
from atst.models.mixins.state_machines import (
    FSMStates, AzureStages, _build_transitions
)


@dataclass
class BaseCSPArgs:
    #{"username": "mock-cloud", "pass": "shh"}
    creds: Dict

@dataclass
class TenantCSPPayload(BaseCSPPayload):
    user_id: str
    password: str
    domain_name: str
    first_name: str
    last_name: str
    country_code: str
    password_recovery_email_address: str


@dataclass
class BillingProfileAddress():
    address: Dict
    """
    "address": {
        "firstName": "string",
        "lastName": "string",
        "companyName": "string",
        "addressLine1": "string",
        "addressLine2": "string",
        "addressLine3": "string",
        "city": "string",
        "region": "string",
        "country": "string",
        "postalCode": "string"
    },
    """
@dataclass
class BillingProfileCLINBudget():
    clinBudget: Dict
    """
        "clinBudget": {
            "amount": 0,
            "startDate": "2019-12-18T16:47:40.909Z",
            "endDate": "2019-12-18T16:47:40.909Z",
            "externalReferenceId": "string"
        }
    """

@dataclass
class BillingProfileCSPPayload(BaseCSPPayload, BillingProfileAddress, BillingProfileCLINBudget):
    displayName: str
    poNumber: str
    invoiceEmailOptIn: str

    """
    {
        "displayName": "string",
        "poNumber": "string",
        "address": {
            "firstName": "string",
            "lastName": "string",
            "companyName": "string",
            "addressLine1": "string",
            "addressLine2": "string",
            "addressLine3": "string",
            "city": "string",
            "region": "string",
            "country": "string",
            "postalCode": "string"
        },
        "invoiceEmailOptIn": true,
        Note: These last 2 are also the body for adding/updating new TOs/clins
        "enabledAzurePlans": [
            {
            "skuId": "string"
            }
        ],
        "clinBudget": {
            "amount": 0,
            "startDate": "2019-12-18T16:47:40.909Z",
            "endDate": "2019-12-18T16:47:40.909Z",
            "externalReferenceId": "string"
        }
    }
    """

@add_state_features(Tags)
class StateMachineWithTags(Machine):
    pass

class PortfolioStateMachine(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin,
    mixins.BaseFSMMixin,
    #mixins.AzureTenantMixin,
    #mixins.AzureBillingProfileMixin,
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
        """
        This is called as a result of a sqlalchemy query.
        Attach a machine depending on the current state.
        """
        self.machine = StateMachineWithTags(
                model = self,
                send_event=True,
                initial=self.state.name if self.state else FSMStates.UNSTARTED.name,
                auto_transitions=False,
                after_state_change='after_state_change',
        )
        states, transitions = _build_transitions(AzureStages)
        self.machine.add_states(self.system_states+states)
        self.machine.add_transitions(self.system_transitions+transitions)

    #@with_payload
    def after_in_progress_callback(self, event):
        stage = 'tenant'
        if stage == 'tenant'
            payload = TenantCSPPayload(
                    creds={"username": "mock-cloud", "pass": "shh"},
                    user_id='123',
                    password='123',
                    domain_name='123',
                    first_name='john',
                    last_name='doe',
                    country_code='US',
                    password_recovery_email_address='password@email.com'
            )
        elif stage == 'billing_profile'
            payload = BillingProfileCSPPayload(
                    creds={"username": "mock-cloud", "pass": "shh"},
            )

        csp = event.kwargs.get('csp')

        if csp is not None:
            self.csp = AzureCSP(app).cloud
        else:
            self.csp = MockCSP(app).cloud

        for attempt in range(5):
            try:
                #response = self.csp.create_tenant(**kwargs)
                response = getattr(self.csp, 'create_'+stage)(payload.__dict__)
            except (ConnectionException, UnknownServerException) as exc:
                print('caught exception. retry', attempt)
                continue
            else: break
        else:
            # failed all attempts
            #self.machine.fail_tenant()
            getattr(self.machine, 'fail_'+stage)()

        if self.portfolio.csp_data is None:
            self.portfolio.csp_data = {}
        self.portfolio.csp_data["tenant_data"] = response
        db.session.add(self.portfolio)
        db.session.commit()

    def is_csp_data_valid(self, event):
        # check portfolio csp details json field for fields

        if self.portfolio.csp_data is None or \
                not isinstance(self.portfolio.csp_data, dict):
            return False

        return all([
            "tenant_data" in self.portfolio.csp_data,
            "tenant_id" in self.portfolio.csp_data['tenant_data'],
            "user_id" in self.portfolio.csp_data['tenant_data'],
            "user_object_id" in self.portfolio.csp_data['tenant_data'],
        ])



    def trigger_next_transition(self, csp):
        state_obj = self.machine.get_state(self.state)

        #FSMStates.UNSTARTED: self.init,
        #FSMStates.STARTING: self.start,
        #FSMStates.STARTED: self

        if state_obj.is_system:
            if self.state == FSMStates.UNSTARTED:
                self.init()

            elif fsm.state == FSMStates.STARTING:
                self.start()

            elif self.state == FSMStates.STARTED:
                # iterate over stages and check the state tag
                #for stage in [st.name for st in list(AzureStages)]:
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
