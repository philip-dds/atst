from enum import Enum

from atst.database import db
from atst.domain.csp.cloud import ConnectionException, UnknownServerException
from atst.domain.csp import MockCSP, AzureCSP

class FSMStageStates(Enum):
    CREATED = "created"
    IN_PROGRESS = "in progress"
    FAILED = "failed"

class AzureFSMStages(Enum):
    TENANT = "tenant"
    BILLING_PROFILE = "billing profile"
    ADMIN_SUBSCRIPTION = "admin subscription"

azure_states = {
    'UNSTARTED' : "unstarted",
    'STARTING' : "starting",
    'STARTED' : "started",
    'COMPLETED' : "completed",
    'FAILED' : "failed",
}
for stage in AzureFSMStages:
    for state in FSMStageStates:
        azure_states[stage.name+"_"+state.name] = stage.value+" "+state.value

FSMStates = Enum('FSMStates', azure_states)

class AzureFSMMixin():

    states_base = [
        {'name': FSMStates.UNSTARTED.name, 'tags': ['system']},
        {'name': FSMStates.STARTING.name, 'tags': ['system']},
        {'name': FSMStates.STARTED.name, 'tags': ['system']},
        {'name': FSMStates.FAILED.name, 'tags': ['system']},
        {'name': FSMStates.COMPLETED.name, 'tags': ['system']},
    ]

    transitions_base = [
        {'trigger': 'init', 
            'source': FSMStates.UNSTARTED, 
            'dest': FSMStates.STARTING
        },
        {'trigger': 'start', 'source': FSMStates.STARTING, 'dest': FSMStates.STARTED},
        {'trigger': 'reset', 'source': '*', 'dest': FSMStates.UNSTARTED},
        {'trigger': 'fail', 'source': '*', 'dest': FSMStates.FAILED,}
    ]


    # getattr(AzureFSMStages, FSMStates.TENANT_IN_PROGRESS.name.split('_')[0]).value


    def _azure_transitions(self):
        transitions = []
        states = []
        compose_state = lambda stage, state: getattr(FSMStates, "_".join([stage.name, state.name]))

        for stage_i, stage in enumerate(AzureFSMStages):
            for state in FSMStageStates:
                states.append(dict(name=compose_state(stage, state), tags=[stage.name, state.name]))
                if state == FSMStageStates.CREATED:
                    if stage_i > 0:
                        src = compose_state(list(AzureFSMStages)[stage_i-1] , FSMStageStates.CREATED)
                    else:
                        src = FSMStates.STARTED
                    transitions.append(
                        dict(
                            trigger='create_'+stage.name.lower(),
                            source=src,
                            dest=compose_state(stage, FSMStageStates.IN_PROGRESS),
                            prepare='prepare_' + stage.name.lower(),
                            before='before_' + stage.name.lower(),
                            after='after_' + stage.name.lower(),
                        )
                    )
                if state == FSMStageStates.IN_PROGRESS:
                    transitions.append(
                        dict(
                            trigger='finish_'+stage.name.lower(),
                            source=compose_state(stage, state),
                            dest=compose_state(stage, FSMStageStates.CREATED),
                            conditions=['is_%s_created' % stage.name.lower()],
                        )
                    )
                if state == FSMStageStates.FAILED:
                    transitions.append(
                        dict(
                            trigger='fail_'+stage.name.lower(),
                            source=compose_state(stage, FSMStageStates.IN_PROGRESS),
                            dest=compose_state(stage, FSMStageStates.FAILED),
                        )
                    )
        return states, transitions

    def prepare_init(self, event): pass
    def before_init(self, event): pass
    def after_init(self, event): pass

    def prepare_start(self, event): pass
    def before_start(self, event): pass
    def after_start(self, event): pass

    def prepare_reset(self, event): pass
    def before_reset(self, event): pass
    def after_reset(self, event): pass



class TenantMixin():

    def prepare_tenant(self, event): pass
    def before_tenant(self, event): pass

    def after_tenant(self, event):
        # enter in_progress state and make api call
        # after state transitions to TENANT_IN_PROGRESS.
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
            self.machine.fail_tenant()

        if self.portfolio.csp_data is None:
            self.portfolio.csp_data = {}
        self.portfolio.csp_data["tenant_data"] = response
        db.session.add(self.portfolio)
        db.session.commit()


    def is_tenant_created(self, event):
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

class BillingProfileMixin:

    def prepare_billing_profile(self, event): pass
    def before_billing_profile(self, event): pass

    def after_billing_profile(self, event):
        # enter in_progress state and make api call
        # after state transitions to BILLING_IN_PROGRESS.

        csp = event.kwargs.get('csp')
        #creds={"username": "mock-cloud", "pass": "shh"}

        if csp is not None:
            self.csp = AzureCSP(app).cloud
        else:
            self.csp = MockCSP(app).cloud

        for attempt in range(5):
            try:
                response = self.csp.create_billing_profile()
                        #{}, '123', **kwargs)
            except (ConnectionException, UnknownServerException) as exc:
                print('caught exception. retry', attempt)
                continue
            else: break
        else:
            # failed all attempts
            self.machine.fail_billing_profile()


        if self.portfolio.csp_data is None:
           self.portfolio.csp_data = {}
        self.portfolio.csp_data["billing_profile_data"] = response
        db.session.add(self.portfolio)
        db.session.commit()

    def is_billing_profile_created(self, event):
        # check portfolio csp details json field for fields

        if self.portfolio.csp_data is None or \
                not isinstance(self.portfolio.csp_data, dict):
            return False

        return all([
            #"tenant_data" in self.portfolio.csp_data,
            #"tenant_id" in self.portfolio.csp_data['tenant_data'],
            #"user_id" in self.portfolio.csp_data['tenant_data'],
            #"user_object_id" in self.portfolio.csp_data['tenant_data'],
        ])

