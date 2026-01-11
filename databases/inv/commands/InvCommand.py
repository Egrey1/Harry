from ..library.modules import View, Button, deps, Context, hybrid_command, Interaction
from ..library.functions import give_army, give_enterprise

class InvCommand:
    @hybrid_command(name='inv', description='Посмотреть свой инвентарь вместе с балансом')
    async def inv(self, ctx: Context | Interaction):
        view = View()
        army = Button(label='Армия', emoji='🪖')
        enterprise = Button(label='Предприятия', emoji='🏭')
        army.callback = give_army
        enterprise.callback = give_enterprise
        country = deps.Country(ctx.author.mention)

        view.add_item(army)
        view.add_item(enterprise)
        await ctx.reply(f'`{country.name if country.name else ctx.author.name}` конкрентизируйте', view=view, ephemeral=True)