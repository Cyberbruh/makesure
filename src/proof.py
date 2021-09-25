import datetime

from dispute import Dispute


class Proof:
    def __init__(self, dispute: Dispute, user: int, description: int) -> None:
        self.id = None
        self.dispute = dispute
        self.user = user
        self.description = description
        self.date = datetime.datetime.now()