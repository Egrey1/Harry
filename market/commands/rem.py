from ..library import Bot, hybrid_command, Context, give_country, Select, SelectOption, View
from ..library.functions import country_positions

class Rem():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_rem", description="Удаляет одну из ваших позиций на рынке")
    async def remove(self, ctx: Context):
        country = await give_country(ctx.author.mention)
        if not country:
            await ctx.reply("Ты даже не страна!")
            return
        
        positions = await country_positions(country)
        if not positions:
            await ctx.reply("У тебя нет позиций на рынке!")
            return
        
        view = View()
        options = [SelectOption(label=item, value=item) for item in positions.keys()]
        select = Select(placeholder="Выбери позицию для удаления", options=options, max_values=1)
        # select.callback = 
        view.add_item(select)