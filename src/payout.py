from datetime import datetime
from enum import Enum
from mongoengine import (
    Document, ReferenceField, IntField, StringField, EnumField, DateTimeField)

from .dispute import Dispute


class PayoutStatus(Enum):
    CREATED = 1
    SUCCESS = 2
    PENDING = 3
    FAILED = 4


class Payout(Document):
    dispute = ReferenceField(Dispute, required=True)
    method = IntField(required=True)
    amount = IntField(required=True)
    data = StringField(required=True)
    payout_id = StringField()
    description = StringField()
    status = EnumField(PayoutStatus, default=PayoutStatus.CREATED)
    date = DateTimeField(default=datetime.utcnow)
