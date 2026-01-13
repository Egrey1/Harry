from ..library import Bot, hybrid_command, Context, deps, Select, SelectOption, View
from ..callbacks import rem_callback

class Rem():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_rem", description="Удаляет одну из ваших позиций на рынке")
    async def remove(self, ctx: Context):
        country = deps.Country(ctx.author.mention)
        if not country:
            await ctx.reply("Ты даже не страна!")
            return
        
        positions = country.market.get_inv()
        if not positions:
            await ctx.reply("У тебя нет позиций на рынке!")
            return
        
        view = View()
        options = [SelectOption(label=item, value=item) for item in positions.keys()]
        select = Select(placeholder="Выбери позицию для удаления", options=options, max_values=1)
        select.callback = lambda interaction: rem_callback(interaction, country)
        view.add_item(select)

        await ctx.send("Так-так... Что там тебе возвращать?", view=view, ephemeral=True)