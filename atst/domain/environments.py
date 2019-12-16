from sqlalchemy import func, or_
from sqlalchemy.orm.exc import NoResultFound
from typing import List
from uuid import UUID

from atst.database import db
from atst.models import (
    Environment,
    Application,
    Portfolio,
    TaskOrder,
    CLIN,
)
from atst.domain.environment_roles import EnvironmentRoles
from atst.utils import update_or_raise_already_exists_error

from .exceptions import NotFoundError, DisabledError


class Environments(object):
    @classmethod
    def create(cls, user, application, name):
        environment = Environment(application=application, name=name, creator=user)
        db.session.add(environment)
        update_or_raise_already_exists_error(message="environment")
        return environment

    @classmethod
    def create_many(cls, user, application, names):
        environments = []
        for name in names:
            environment = Environments.create(user, application, name)
            environments.append(environment)

        db.session.add_all(environments)
        return environments

    @classmethod
    def update(cls, environment, name=None):
        if name is not None:
            environment.name = name
            db.session.add(environment)
            update_or_raise_already_exists_error(message="environment")
            return environment

    @classmethod
    def get(cls, environment_id):
        try:
            env = (
                db.session.query(Environment)
                .filter_by(id=environment_id, deleted=False)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("environment")

        return env

    @classmethod
    def update_env_role(cls, environment, application_role, new_role):
        env_role = EnvironmentRoles.get_for_update(application_role.id, environment.id)

        if env_role and new_role and (env_role.disabled or env_role.deleted):
            raise DisabledError("environment_role", env_role.id)

        if env_role and env_role.role != new_role and not env_role.disabled:
            env_role.role = new_role
            db.session.add(env_role)
        elif not env_role and new_role:
            env_role = EnvironmentRoles.create(
                application_role=application_role,
                environment=environment,
                role=new_role,
            )
            db.session.add(env_role)

        if env_role and not new_role and not env_role.disabled:
            EnvironmentRoles.disable(env_role.id)

        db.session.commit()

    @classmethod
    def revoke_access(cls, environment, target_user):
        EnvironmentRoles.delete(environment.id, target_user.id)

    @classmethod
    def delete(cls, environment, commit=False):
        environment.deleted = True
        db.session.add(environment)

        for role in environment.roles:
            role.deleted = True
            db.session.add(role)

        if commit:
            db.session.commit()

        # TODO: How do we work around environment deletion being a largely manual process in the CSPs

        return environment

    @classmethod
    def base_provision_query(cls, now):
        return (
            db.session.query(Environment.id)
            .join(Application)
            .join(Portfolio)
            .join(TaskOrder)
            .join(CLIN)
            .filter(CLIN.start_date <= now)
            .filter(CLIN.end_date > now)
            .filter(Environment.deleted == False)
            .filter(
                or_(
                    Environment.claimed_until == None,
                    Environment.claimed_until <= func.now(),
                )
            )
        )

    @classmethod
    def get_environments_pending_creation(cls, now) -> List[UUID]:
        """
        Any environment with an active CLIN that doesn't yet have a `cloud_id`.
        """
        results = (
            cls.base_provision_query(now).filter(Environment.cloud_id == None).all()
        )
        return [id_ for id_, in results]

    @classmethod
    def get_environments_pending_atat_user_creation(cls, now) -> List[UUID]:
        """
        Any environment with an active CLIN that has a cloud_id but no `root_user_info`.
        """
        results = (
            cls.base_provision_query(now)
            .filter(Environment.cloud_id != None)
            .filter(Environment.root_user_info == None)
        ).all()
        return [id_ for id_, in results]
