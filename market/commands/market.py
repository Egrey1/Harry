from ..library import Cog, Bot, hybrid_command, Context, Embed, deps
from ..library.modules import con, Row

class Market():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market", description="Просмотр рынка")
    async def dmarket(self, ctx: Context):
        # Inline summary of market table
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute("""
                       SELECT * 
                       FROM market
                       """)
        rows = cursor.fetchall()
        connect.close()

        market: dict[str, dict] = {}

        for row in rows:
            r = dict(row)
            country = r.get('name')
            for key, value in r.items():
                if key == 'name' or not value:
                    continue
                try:
                    qty_str, price_str = str(value).split()
                    qty = int(qty_str)
                    price = int(price_str)
                except Exception:
                    continue

                if qty <= 0:
                    continue

                if key not in market:
                    market[key] = {'total': 0, 'sellers': []}

                market[key]['total'] += qty
                market[key]['sellers'].append({'country': country, 'price': price, 'qty': qty})

        if not market:
            await ctx.send("Пока что никто ничего не продает", ephemeral=True)
            return

        desc = ''

        for item, details in market.items():
            desc += f"### {item} - {details['total']}\n"

            sm, count = 0, 0

            for sellers in details['sellers']:
                desc += f'{sellers["country"]} - {sellers["qty"]} по __`{deps.CURRENCY}{sellers["price"]}`__\n'
                sm += sellers["price"]
                count += 1
            avg = (sm / count) if count else 0
            desc += f'Средняя цена: __`{deps.CURRENCY}{avg:.2f}`__\n\n\n'

        embed = Embed(title="Рынок товаров", description=desc)
        await ctx.send(embed=embed, ephemeral=True)