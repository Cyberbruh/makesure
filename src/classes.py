import datetime
import enum


class DisputeStatus(enum.Enum):
    CREATED = 1
    ACCEPTED = 2
    REJECTED = 3
    PENDING = 4
    TIE = 5
    WIN1 = 6
    WIN2 = 7
    REPORTED = 8


class Dispute:
    def __init__(self, user1: int, user2: int, description: str, amount: int) -> None:
        self.id = None
        self.user1 = user1
        self.user2 = user2
        self.description = description
        self.amount = amount
        self.date = datetime.datetime.now()


class Proof:
    def __init__(self, dispute: Dispute, user: int, description: int) -> None:
        self.id = None
        self.dispute = dispute
        self.user = user
        self.description = description
        self.date = datetime.datetime.now()


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
