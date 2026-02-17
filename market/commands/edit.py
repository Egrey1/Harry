from ..library import Bot, hybrid_command, Context, SelectOption, Select, View, deps
from ..callbacks import edit_callback

class Edit():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_edit", description="Редактирует одну из ваших позиций на рынке")
    async def edit(self, ctx: Context):
        country = deps.Country(ctx.author.mention)
        
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

        if not country:
            await ctx.send("Вы не зарегистрированы!", ephemeral=True)
            return
        
        # Build positions from Country.market
        positions = {name: f"{item.quantity} {item.price}" for name, item in country.market.inventory.items() if item.quantity > 0}
        if not positions: 
            await ctx.send("Нет у вас на рынке ничего!", ephemeral=True)
            return
        
        view = View()
        options = []
        for item, value in positions.items():
            have_item = country.inventory.get(item)
            have = have_item.quantity if have_item else 0
            qty, price = value.split()
            options.append(SelectOption(label=f'{item} - {qty}', description=f"У вас есть {have}, каждая по {deps.CURRENCY}{price}"))
        
        select = Select(placeholder="И какую позицию вам нужно отредактировать?", options=options)
        select.callback = edit_callback
        view.add_item(select)

        await ctx.send("Все! Выбирай!", view=view, ephemeral=True)