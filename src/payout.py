from datetime import datetime
from enum import Enum
from mongoengine import (
    Document, ReferenceField, IntField, StringField, EnumField, DateTimeField, FloatField)

from .dispute import Dispute


class Payout(Document):
    dispute = ReferenceField(Dispute, required=True)
    amount = FloatField(required=True)
    data = StringField(required=True)
    date = DateTimeField(default=datetime.utcnow)
