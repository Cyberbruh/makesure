from datetime import datetime
from enum import Enum
from mongoengine import (
    Document, ReferenceField, IntField, StringField, EnumField, DateTimeField)

from .dispute import Dispute


class PayoutStatus(Enum):
    CREATED = 1
    SUCCESS = 2


class Payout(Document):
    dispute = ReferenceField(Dispute, required=True)
    method = IntField(required=True)
    data = StringField(required=True)
    status = EnumField(PayoutStatus, default=PayoutStatus.CREATED)
    date = DateTimeField(default=datetime.utcnow)
