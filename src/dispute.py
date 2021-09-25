from datetime import *
from enum import *
from mongoengine import *

class DisputeStatus(Enum):
    CREATED = 1
    ACCEPTED = 2
    REJECTED = 3
    PENDING = 4
    TIE = 5
    WIN1 = 6
    WIN2 = 7
    REPORTED = 8

class Dispute(Document):
    user1_id = IntField(required=True)
    user2_id = IntField(required=True)
    description = StringField(required=True)
    amount = IntField(required=True)
    status = EnumField(DisputeStatus, default=DisputeStatus.CREATED)
    date = DateTimeField(default=datetime.utcnow)
