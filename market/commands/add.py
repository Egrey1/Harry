from ..library import Bot, hybrid_command, Context, View, SelectOption, Select, deps
from ..callbacks import add_callback

class Add():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_add", description="Добавляет вашу позицию на рынок")
    async def add(self, ctx: Context):
        country = deps.Country(ctx.author.mention)

        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

        if not country:
            await ctx.send('Ты не зарегистрирован!', ephemeral=True)
            return
        
        # Use Country object inventory directly
        items = {k: v.quantity for k, v in country.inventory.items()}

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