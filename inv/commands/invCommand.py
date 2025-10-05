from ..library.modules import commands, View, Button, give_country
from ..library.functions import give_army, give_enterprise

class InvCommand:
    # Показывает инвентарь страны 
    @commands.command()
    async def inv(self, ctx: commands.Context):
        view = View()
        army = Button(label='Армия', emoji='🪖')
        enterprise = Button(label='Предприятия', emoji='🏭')
        army.callback = give_army
        enterprise.callback = give_enterprise

        view.add_item(army)
        view.add_item(enterprise)
        await ctx.reply(f'`{await give_country(ctx.author.mention) if await give_country(ctx.author.mention) else ctx.author.name}` конкрентизируйте', view=view, ephemeral=True)
