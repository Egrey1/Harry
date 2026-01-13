from ..library import Bot, hybrid_command, Context, View, Select, SelectOption, deps, List
from ..callbacks import buy_callback
from ..library.modules import con, Row

class Buy():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_buy", description="Покупка вооружения с рынка")
    async def buy(self, ctx: Context):
        country = deps.Country(ctx.author.mention)

        # Inline market summary
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute("""
                       SELECT * 
                       FROM market
                       """)
        rows = cursor.fetchall()
        connect.close()

        positions: dict[str, dict[str, str]] = {}

        for row in rows:
            r = dict(row)
            country_name = r.get('name')
            for name, value in r.items():
                if name == 'name' or not value:
                    continue
                try:
                    qty_str, price_str = str(value).split()
                    qty = int(qty_str)
                    price = int(price_str)
                except Exception:
                    continue

                if qty <= 0:
                    continue

                if name not in positions:
                    positions[name] = {'total': 0, 'sellers': []}

                positions[name]['total'] += qty
                positions[name]['sellers'].append({'country': country_name, 'price': price, 'qty': qty})

        if not positions:
            await ctx.send(f'На рынке нет доступных позиций для покупки!')
            return

        view = View()
        options = []
        for item in positions.keys():
            options.append(SelectOption(label=f"{item} - {positions[item]['total']}"))
        
        select = Select(placeholder='Выберите позицию для покупки', options=options)
        select.callback = lambda interaction: buy_callback(interaction, country, positions)
        view.add_item(select)

        await ctx.send('Выберите позицию для покупки с рынка:', view=view, ephemeral=True)
