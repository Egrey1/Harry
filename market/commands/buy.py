from ..library import Bot, hybrid_command, Context, give_country, View, Select, SelectOption
from ..library.functions import market_summary
from ..callbacks import buy_callback

class Buy():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_buy", description="Покупка вооружения с рынка")
    async def buy(self, ctx: Context):
        country = await give_country(ctx.author.mention)

        positions = await market_summary()
        if not positions:
            await ctx.send(f'На рынке нет доступных позиций для покупки!')
            return


        view = View()
        options = []
        for item in positions.keys():
            options.append(SelectOption(label=f'{item} - {positions[item]['total']}'))
        
        select = Select(placeholder='Выберите позицию для покупки', options=options)
        select.callback = lambda interaction: buy_callback(interaction, country, positions)
        view.add_item(select)

        await ctx.send('Выберите позицию для покупки с рынка:', view=view, ephemeral=True)
