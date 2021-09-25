from datetime import *
from enum import *
from mongoengine import *

from .dispute import Dispute

class DepositStatus(Enum):
    CREATED = 1
    LINK_SENT = 2
    SUCCESS = 3

class Deposit(Document):
    user_id = IntField(required=True)
    disput = ReferenceField(Dispute)
    method = IntField(required=True)
    payment_link = StringField(required=True)
    status = EnumField(DepositStatus, default=DepositStatus.CREATED)
    date = DateTimeField(default=datetime.utcnow)
