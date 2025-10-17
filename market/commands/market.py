from ..library import Cog, Bot, hybrid_command, Context, Embed, CURRENCY
from ..library.functions import market_summary

class Market():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market", description="Просмотр рынка")
    async def dmarket(self, ctx: Context):
        market = await market_summary()
        if not market:
            await ctx.send("Пока что никто ничего не продает", ephemeral=True)
            return
        
        desc = ''

        for item, details in market.items():
            desc += f"### {item} - {details['total']}\n"

            sm, count = 0, 0

            for sellers in details['sellers']:
                desc += f'{sellers["country"]} - {sellers["qty"]} по __`{CURRENCY}{sellers["price"]}`__\n'
                sm += sellers["price"]
                count += 1
            avg = (sm // count) if count else 0
            desc += f'Средняя цена: __`{CURRENCY}{avg}`__\n\n\n'

        embed = Embed(title="Рынок товаров", description=desc)
        await ctx.send(embed=embed, ephemeral=True)