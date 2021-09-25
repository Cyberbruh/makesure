def addDispute(db, dispute):
    id = db.disputes.insert_one(dispute).inserted_id
    return id

