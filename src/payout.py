import datetime
import enum

from dispute import Dispute


class PayoutStatus(enum.Enum):
    CREATED = 1
    SUCCESS = 2


class Payout:
    def __init__(self, user: int, dispute: Dispute, payment_method: int, data: str) -> None:
        self.id = None
        self.user = user
        self.dispute = dispute
        self.payment_method = payment_method
        self.status = PayoutStatus.CREATED
        self.date = datetime.datetime.now()
