from ..library.modules import Context, hybrid_command, deps, Embed


class BalCommand:

    @hybrid_command(name='bal', description='Посмотреть свой баланс')
    async def bal(self, ctx: Context) -> None:
        country = deps.Country(ctx.author.mention)
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
        

        if not country:
            if ctx.interaction:
                await ctx.interaction.followup.send('Вы не страна!', ephemeral= True)
            else:
                await ctx.reply('Вы не страна!')
            return None
        

        money = country.balance
        embed = Embed()
        embed.title = f'Ваш баланс равен: {deps.CURRENCY}{money}'
        embed.description = f"""
        Вы зарабатываете {deps.CURRENCY}{country.get_earnings()} в месяц
        Вы тратите {deps.CURRENCY}{country.get_expenses()} в месяц\nВаш чистый доход: {deps.CURRENCY}{country.get_earnings() - country.get_expenses()} в месяц
        
        {'О нет! Похоже, что вы теряете деньги каждый месяц! Это означает, что производительность ваших фабрик замедлено. Производство самых совершенных боевых единиц и вовсе остановлено! Срочно исправьте это, создав офисы или открыв промышленные зоны!' if country.get_earnings() - country.get_expenses() < 0 else ''}"""
        embed.set_footer(text='Вы можете посмотреть свой инвентарь с помощью команды /inv')
        
        if ctx.interaction:
            await ctx.interaction.followup.send(embed=embed, ephemeral= True)
        else:
            await ctx.reply(embed=embed)
        return None