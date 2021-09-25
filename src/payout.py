from datetime import *
from enum import *
from mongoengine import *

from .dispute import Dispute

class PayoutStatus(Enum):
    CREATED = 1
    SUCCESS = 2

class Payout(Document):
    dispute = ReferenceField(Dispute)
    method = IntField(required=True)
    data = StringField(required=True)
    status = EnumField(PayoutStatus, default=PayoutStatus.CREATED)
    date = DateTimeField(default=datetime.utcnow)
