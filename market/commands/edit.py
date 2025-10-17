from ..library import Cog, Bot, hybrid_command, Context, give_country, SelectOption, CURRENCY, Select, View
from ..library.functions import country_positions, give_items
from ..callbacks import edit_callback

class EditCommand():
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_edit", description="Редактирует одну из ваших позиций на рынке")
    async def edit(self, ctx: Context):
        country = await give_country(ctx.author.mention)
        if not country:
            await ctx.send("Вы не зарегистрированы!", ephemeral=True)
            return
        
        positions = await country_positions(country)
        if not positions: 
            await ctx.send("Нет у вас на рынке ничего!", ephemeral=True)
            return
        
        
        view = View()
        options = []
        for item, value in positions.items():
            have = await give_items(country, item)
            qty, price = value.split()
            options.append(SelectOption(label=f'{item} - {qty}', description=f"У вас есть {have}, каждая по {CURRENCY}{price}"))
        
        select = Select(placeholder="И какую позицию вам нужно отредактировать?", options=options)
        select.callback = edit_callback
        view.add_item(select)

        await ctx.send("Все! Выбирай!", view=view, ephemeral=True)