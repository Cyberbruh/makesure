import datetime
import enum

from dispute import Dispute


class DepositStatus(enum.Enum):
    CREATED = 1
    LINK_SENT = 2
    SUCCESS = 3


class Deposit:
    def __init__(self, db, user_id: int, dispute: Dispute, payment_method: int) -> None:
        self.user = user_id
        self.dispute = dispute.id
        self.payment_method = payment_method
        self.status = DepositStatus.CREATED
        self.date = datetime.datetime.now()
        self.id = db.deposites.insert_one(self.__dict__).inserted_id