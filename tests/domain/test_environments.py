import pytest
import pendulum

from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.exceptions import NotFoundError
from atst.models.environment_role import CSPRole

from tests.factories import (
    ApplicationFactory,
    PortfolioFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    ApplicationRoleFactory,
    TaskOrderFactory,
    CLINFactory,
)


@pytest.mark.skip(reason="Reinstate and update once jobs api is up")
def test_create_environments():
    application = ApplicationFactory.create()
    environments = Environments.create_many(application, ["Staging", "Production"])
    for env in environments:
        assert env.cloud_id is not None


def test_update_env_role():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)
    new_role = CSPRole.TECHNICAL_READ.value

    assert Environments.update_env_role(
        env_role.environment, env_role.application_role, new_role
    )
    assert env_role.role == new_role


def test_update_env_role_no_access():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)

    assert Environments.update_env_role(
        env_role.environment, env_role.application_role, None
    )
    assert not EnvironmentRoles.get(
        env_role.application_role.id, env_role.environment.id
    )


def test_update_env_role_no_change():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)
    new_role = CSPRole.BASIC_ACCESS.value

    assert not Environments.update_env_role(
        env_role.environment, env_role.application_role, new_role
    )


def test_update_env_roles_by_environment():
    environment = EnvironmentFactory.create()
    app_role_1 = ApplicationRoleFactory.create(application=environment.application)
    env_role_1 = EnvironmentRoleFactory.create(
        application_role=app_role_1,
        environment=environment,
        role=CSPRole.BASIC_ACCESS.value,
    )
    app_role_2 = ApplicationRoleFactory.create(application=environment.application)
    env_role_2 = EnvironmentRoleFactory.create(
        application_role=app_role_2,
        environment=environment,
        role=CSPRole.NETWORK_ADMIN.value,
    )
    app_role_3 = ApplicationRoleFactory.create(application=environment.application)
    env_role_3 = EnvironmentRoleFactory.create(
        application_role=app_role_3,
        environment=environment,
        role=CSPRole.TECHNICAL_READ.value,
    )

    team_roles = [
        {
            "application_role_id": app_role_1.id,
            "user_name": app_role_1.user_name,
            "role_name": CSPRole.BUSINESS_READ.value,
        },
        {
            "application_role_id": app_role_2.id,
            "user_name": app_role_2.user_name,
            "role_name": CSPRole.NETWORK_ADMIN.value,
        },
        {
            "application_role_id": app_role_3.id,
            "user_name": app_role_3.user_name,
            "role_name": None,
        },
    ]

    Environments.update_env_roles_by_environment(environment.id, team_roles)
    assert env_role_1.role == CSPRole.BUSINESS_READ.value
    assert env_role_2.role == CSPRole.NETWORK_ADMIN.value
    assert not EnvironmentRoles.get(app_role_3.id, environment.id)


def test_get_excludes_deleted():
    env = EnvironmentFactory.create(
        deleted=True, application=ApplicationFactory.create()
    )
    with pytest.raises(NotFoundError):
        Environments.get(env.id)


def test_delete_environment(session):
    env = EnvironmentFactory.create(application=ApplicationFactory.create())
    env_role = EnvironmentRoleFactory.create(
        application_role=ApplicationRoleFactory.create(application=env.application),
        environment=env,
    )
    assert not env.deleted
    assert not env_role.deleted
    Environments.delete(env)
    assert env.deleted
    assert env_role.deleted
    # did not flush
    assert session.dirty

    Environments.delete(env, commit=True)
    assert env.deleted
    assert env_role.deleted
    # flushed the change
    assert not session.dirty


def test_update_environment():
    environment = EnvironmentFactory.create()
    assert environment.name is not "name 2"
    Environments.update(environment, name="name 2")
    assert environment.name == "name 2"


class TestGetEnvironmentsPendingCreate:
    NOW = pendulum.now()
    YESTERDAY = NOW.subtract(days=1)
    TOMORROW = NOW.add(days=1)

    def create_portfolio_with_clins(self, start_and_end_dates):
        return PortfolioFactory.create(
            applications=[
                {
                    "name": "Mos Eisley",
                    "description": "Where Han shot first",
                    "environments": [{"name": "thebar"}],
                }
            ],
            task_orders=[
                TaskOrderFactory.create(
                    clins=[
                        CLINFactory.create(start_date=start_date, end_date=end_date)
                        for (start_date, end_date) in start_and_end_dates
                    ]
                )
            ],
        )

    def test_with_expired_clins(self, session):
        self.create_portfolio_with_clins([(self.YESTERDAY, self.YESTERDAY)])
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 0

    def test_with_active_clins(self, session):
        portfolio = self.create_portfolio_with_clins([(self.YESTERDAY, self.TOMORROW)])
        Environments.get_environments_pending_creation(self.NOW) == [
            portfolio.applications[0].environments[0].id
        ]

    def test_with_future_clins(self, session):
        self.create_portfolio_with_clins([(self.TOMORROW, self.TOMORROW)])
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 0
