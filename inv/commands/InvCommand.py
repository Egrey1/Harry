from ..library.modules import View, Button, give_country, Context, hybrid_command
from ..library.functions import give_army, give_enterprise

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