import datetime
import enum

from dispute import Dispute


class DepositStatus(enum.Enum):
    CREATED = 1
    LINK_SENT = 2
    SUCCESS = 3


class Deposit:
    def __init__(self, user: int, dispute: Dispute, payment_method: int) -> None:
        self.id = None
        self.user = user
        self.dispute = dispute
        self.payment_method = payment_method
        self.status = DepositStatus.CREATED
        self.date = datetime.datetime.now()