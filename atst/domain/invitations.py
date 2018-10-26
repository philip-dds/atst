import datetime
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.invitation import Invitation, Status as InvitationStatus

from .exceptions import NotFoundError


class InvitationError(Exception):
    def __init__(self, invite):
        self.invite = invite

    @property
    def message(self):
        return "{} has a status of {}".format(self.invite.id, self.invite.status.value)


class Invitations(object):
    # number of minutes a given invitation is considered valid
    EXPIRATION_LIMIT_MINUTES = 360

    @classmethod
    def _get(cls, invite_id):
        try:
            invite = db.session.query(Invitation).filter_by(id=invite_id).one()
        except NoResultFound:
            raise NotFoundError("invite")

        return invite

    @classmethod
    def create(cls, workspace, inviter, user):
        invite = Invitation(
            workspace=workspace,
            inviter=inviter,
            user=user,
            status=InvitationStatus.PENDING,
            expiration_time=Invitations.current_expiration_time(),
        )
        db.session.add(invite)
        db.session.commit()

        return invite

    @classmethod
    def accept(cls, invite_id):
        invite = Invitations._get(invite_id)

        if invite.is_expired:
            invite.status = InvitationStatus.REJECTED
        elif invite.is_pending:
            invite.status = InvitationStatus.ACCEPTED

        db.session.add(invite)
        db.session.commit()

        if invite.is_revoked or invite.is_rejected:
            raise InvitationError(invite)

        return invite

    @classmethod
    def current_expiration_time(cls):
        return datetime.datetime.now() + datetime.timedelta(
            minutes=Invitations.EXPIRATION_LIMIT_MINUTES
        )
