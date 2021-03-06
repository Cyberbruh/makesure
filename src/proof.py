from datetime import datetime
from mongoengine import (
    Document, ReferenceField, IntField, StringField, DateTimeField)

from .dispute import Dispute


class Proof(Document):
    dispute = ReferenceField(Dispute, required=True)
    user_id = IntField(required=True)
    description = StringField(required=True)
    date = DateTimeField(default=datetime.utcnow)