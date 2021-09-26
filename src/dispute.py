from datetime import datetime
from enum import Enum
from mongoengine import (
    Document, IntField, StringField, EnumField, DateTimeField)


class DisputeStatus(Enum):
    CREATED = 1 # только созданный спор
    ACCEPTED = 2 # принятый спор
    REJECTED = 3 # отклоненный спор
    PENDING = 4 # после оплаты обоих
    TIE = 5 # ничья
    WIN1 = 6
    WIN2 = 7
    REPORTED = 8 # отправлен на судейство
    JUDGING = 9 # в процессе рассмотрения
    EVIDENCE = 10 # сбор доказательств
    CANCELED = 11


class Dispute(Document):
    user1_id = IntField(required=True)
    user2_id = IntField(required=True)
    requisites1 = StringField()
    requisites2 = StringField()
    description = StringField(required=True)
    amount = IntField(required=True)
    status = EnumField(DisputeStatus, default=DisputeStatus.CREATED)
    date = DateTimeField(default=datetime.utcnow)
