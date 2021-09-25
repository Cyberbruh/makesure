from datetime import *
from mongoengine import *

from .dispute import Dispute

class Proof(Document):
    dispute = ReferenceField(Dispute)
    user_id = IntField(required=True)
    description = StringField()
    date = DateTimeField(default=datetime.utcnow)