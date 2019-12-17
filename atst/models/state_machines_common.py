from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship

#from transitions import Machine
from transitions.extensions.states import add_state_features, Timeout

from atst.models.base import Base
import atst.models.mixins as mixins
import atst.models.types as types
from atst.database import db

@add_state_features(Timeout)
class APICallFSM(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin
):
    """
    Generic Finite State Machine that is responsible for handling an API call state

    """
    __tablename__ = "api_call_state_machines"

    id = types.Id()
    machine_instance = Column(types.PickleType)

    states = [
        "init",
        {'name': "in_progress", 'timeout': 30, 'on_timeout': 'handle_timeout'},
        "failed",
        "completed",
    ]

    def save(self):
        """
        write to db
        """
        pass

    def handle_timeout(self):
        """
        A timeout is triggered in a thread.
        This implies several limitations (e.g. catching Exceptions raised in timeouts).
        Consider an event queue for more sophisticated applications.
        """
        #TODO record event and transitionto 'failed'
        pass


