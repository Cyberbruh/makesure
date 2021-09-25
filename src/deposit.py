from datetime import datetime
from enum import Enum
from mongoengine import (
    Document, IntField, ReferenceField, StringField, EnumField, DateTimeField, FloatField)

from .dispute import Dispute


class DepositStatus(Enum):
    CREATED = 1
    LINK_SENT = 2
    SUCCESS = 3
    CANCELED = 4


class Deposit(Document):
    user_id = IntField(required=True)
    dispute = ReferenceField(Dispute, required=True)
    method = IntField(required=True)
    payment_url = StringField()
    invoice_id = StringField()
    coin_amount = FloatField()
    status = EnumField(DepositStatus, default=DepositStatus.CREATED)
    date = DateTimeField(default=datetime.utcnow)
