from ..library import Cog, Bot, hybrid_command, Context, give_country, View, SelectOption, Select
from ..library.functions import give_items
from ..callbacks import add_callback

class AddCommand():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_add", description="Добавляет вашу позицию на рынок")
    async def add(self, ctx: Context):
        country = await give_country(ctx.author.mention)

        if not country:
            await ctx.send('Ты не зарегистрирован!', ephemeral=True)
            return
        
        items = await give_items(country)

        view = View()
        options = []

        for item, count in items.items():
            if count > 0:
                if item not in ('Пехота', 'Морпехота', 'Десантник', 'Кавалерия'):
                    options.append(SelectOption(label=f'{item} - {count}', value=item))
        if not options:
            await ctx.send('Ты в начале инвентарь свой пополни!', ephemeral=True)
            return
        
        select = Select(placeholder='Выбирайте, не стесняйтесь!', options=options)
        select.callback = add_callback
        view.add_item(select)

        await ctx.send('Что вы хотите добавить на рынок?', view=view, ephemeral=True)