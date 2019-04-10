import pytest

from atst.domain.applications import Applications
from atst.domain.exceptions import NotFoundError

from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    UserFactory,
    PortfolioFactory,
    EnvironmentFactory,
)


def test_create_application_with_multiple_environments():
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio, "My Test Application", "Test", ["dev", "prod"]
    )

    assert application.portfolio == portfolio
    assert application.name == "My Test Application"
    assert application.description == "Test"
    assert sorted(e.name for e in application.environments) == ["dev", "prod"]


def test_portfolio_owner_can_view_environments():
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[{"environments": [{"name": "dev"}, {"name": "prod"}]}],
    )
    application = Applications.get(portfolio.applications[0].id)

    assert len(application.environments) == 2


def test_can_only_update_name_and_description():
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[
            {
                "name": "Application 1",
                "description": "a application",
                "environments": [{"name": "dev"}],
            }
        ],
    )
    application = Applications.get(portfolio.applications[0].id)
    env_name = application.environments[0].name
    Applications.update(
        application,
        {
            "name": "New Name",
            "description": "a new application",
            "environment_name": "prod",
        },
    )

    assert application.name == "New Name"
    assert application.description == "a new application"
    assert len(application.environments) == 1
    assert application.environments[0].name == env_name


def test_get_excludes_deleted():
    app = ApplicationFactory.create(deleted=True)
    with pytest.raises(NotFoundError):
        Applications.get(app.id)


def test_delete_application(session):
    app = ApplicationFactory.create()
    app_role = ApplicationRoleFactory.create(user=UserFactory.create(), application=app)
    env1 = EnvironmentFactory.create(application=app)
    env2 = EnvironmentFactory.create(application=app)
    assert not app.deleted
    assert not env1.deleted
    assert not env2.deleted
    assert not app_role.deleted

    Applications.delete(app)

    assert app.deleted
    assert env1.deleted
    assert env2.deleted
    assert app_role.deleted

    # changes are flushed
    assert not session.dirty
