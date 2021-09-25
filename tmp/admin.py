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
    test_count = Proof.objects(Q(user_id=dispute.user1_id) & Q(dispute=dispute)).count()
    if(test_count == 0 or test_count > 1):
        raise Exception('Not enough or too many proofs for 1st user')
    proof1 = Proof.objects(Q(user_id=dispute.user1_id) & Q(dispute=dispute.id)).first()
    await ctx.author.send('Участник 1')
    await ctx.author.send(proof1.description)
    test_count = Proof.objects(Q(user_id=dispute.user2_id) & Q(dispute=dispute)).count()
    if(test_count == 0 or test_count > 1):
        raise Exception('Not enough or too many proofs for 2nd user')
    proof2 = Proof.objects(Q(user_id=dispute.user2_id) & Q(dispute=dispute.id)).first()
    await ctx.author.send('Участник 2')
    await ctx.author.send(proof2.description)
    await ctx.author.send(embed=discord.Embed(title='Решение?'), components=[[
        Button(style=ButtonStyle.green, label='Участник 1', custom_id=str(time.time() + 1)),
        Button(style=ButtonStyle.green, label='Участник 2', custom_id=str(time.time() + 2)),
        Button(style=ButtonStyle.green, label='Ничья', custom_id=str(time.time() + 3))
    ]])
    res = await bot.wait_for('button_click', check= lambda msg: (msg.author == ctx.author) & isinstance(msg.channel, discord.DMChannel))
    if res.component.label == 'Участник 1':
        result = 1
    elif res.component.label == 'Участник 2':
        result = 2
    else:
        result = 0
    await res.respond(content='Спор разрешён! Спасибо!')
    await solveDispute(result, dispute)

async def solveDispute(result, dispute):
    if(result == 1):
        dispute.status = DisputeStatus.WIN1
    elif(result == 2):
        dispute.status = DisputeStatus.WIN2
    else:
        dispute.status = DisputeStatus.TIE
    print(result)
    #dispute.save()