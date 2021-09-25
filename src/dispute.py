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
    def __init__(self, db, user1_id: int, user2_id: int, description: str, amount: int) -> None:
        self.user1 = user1_id
        self.user2 = user2_id
        self.description = description
        self.amount = amount
        self.date = datetime.datetime.now()
        self.status = DisputeStatus.CREATED
        self.id = db.disputes.insert_one(self.__dict__).inserted_id
