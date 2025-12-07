from .library.modules import View, Button, give_country, Context, hybrid_command, CURRENCY, get_money
from .library.functions import give_army, give_enterprise

class InvCommand:
    @hybrid_command(name='inv', description='Посмотреть свой инвентарь вместе с балансом')
    async def inv(self, ctx: Context):
        view = View()
        army = Button(label='Армия', emoji='🪖')
        enterprise = Button(label='Предприятия', emoji='🏭')
        army.callback = give_army
        enterprise.callback = give_enterprise

        view.add_item(army)
        view.add_item(enterprise)
        await ctx.reply(f'`{await give_country(ctx.author.mention) if await give_country(ctx.author.mention) else ctx.author.name}` конкрентизируйте', view=view, ephemeral=True)

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