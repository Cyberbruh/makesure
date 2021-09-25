@bot.command(name="admin")
async def admin(ctx):
    """
    Admin command. Admin starts to look up reported disputes
    """
    if "admin" in [y.name.lower() for y in ctx.author.roles]:
        while(Dispute.objects(Q(status=DisputeStatus.REPORTED) | Q(status=DisputeStatus.JUDGING)).count()):
            await startReportCheck(ctx)

async def startReportCheck(ctx):
    dispute = Dispute.objects(Q(status=DisputeStatus.REPORTED) | Q(status=DisputeStatus.JUDGING)).first()
    if dispute is None:
        return
    await ctx.author.send('Решаем спор номер:'+str(dispute.id))
    dispute.status = DisputeStatus.JUDGING;
    dispute.save()
    test_count = Proof.objects(Q(user_id=dispute.user1_id) | Q(dispute=dispute)).count()
    print(test_count)
    if(test_count == 0 or test_count > 1):
        raise Exception('Too many proofs for 1 user')
    proof1 = Proof.objects(Q(user_id=dispute.user1_id) | Q(dispute=dispute.id)).first()
    print(proof1.id)
    #await ctx.author.send('Участник 1')
    # await usr.send('Участник 1')