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
