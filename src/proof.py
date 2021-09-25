import datetime

from .dispute import Dispute

class Proof:
    def __init__(self, db, dispute: Dispute, user_id: int, description: int) -> None:
        self.dispute = dispute.id
        self.user_id = user_id
        self.description = description
        self.date = datetime.datetime.now()
        self.id = db.proofs.insert_one(self.__dict__).inserted_id