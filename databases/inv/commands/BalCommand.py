from ..library.modules import Context, hybrid_command, deps


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
        
        if ctx.interaction:
            await ctx.interaction.followup.send(f'Ваш баланс равен {deps.CURRENCY}{money}', ephemeral= True)
        else:
            await ctx.reply(f'Ваш баланс равен {deps.CURRENCY}{money}')
        return None