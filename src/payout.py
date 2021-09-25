import datetime
import enum

from .dispute import Dispute


class PayoutStatus(enum.Enum):
    CREATED = 1
    SUCCESS = 2


class Payout:
    def __init__(self, db, user_id: int, dispute: Dispute, payment_method: int, data: str) -> None:
        self.id = None
        self.user = user_id
        self.dispute_id = dispute.id
        self.payment_method = payment_method
        self.status = PayoutStatus.CREATED
        self.data = data
        self.date = datetime.datetime.now()
        self.id = db.payouts.insert_one(self.__dict__).inserted_id