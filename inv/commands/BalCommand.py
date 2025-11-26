from .inv.library.modules import give_country, Context, hybrid_command, CURRENCY, get_money


class BalCommand:

    @hybrid_command(name='bal', description='Посмотреть свой баланс')
    async def bal(self, ctx: Context) -> None:
        country = await give_country(ctx.author.mention)
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
        

        if not country:
            if ctx.interaction:
                await ctx.interaction.followup.send('Вы не страна!', ephemeral= True)
            else:
                await ctx.reply('Вы не страна!')
            return None
        

        money = await get_money(country)
        
        if ctx.interaction:
            await ctx.interaction.followup.send(f'Ваш баланс равен {CURRENCY}{money}', ephemeral= True)
        else:
            await ctx.reply(f'Ваш баланс равен {CURRENCY}{money}')
        return None