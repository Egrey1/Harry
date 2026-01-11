from ..library.modules import (hybrid_command, Context, View, Select, SelectOption,
                               deps)
from ..library.callbacks import use_callback

class UseCommand:
    @hybrid_command(name='use', description='Убрать предмет')
    async def use(self, ctx: Context) -> None:
        country = deps.Country(ctx.author.mention)
        if not country:
            await ctx.reply('Вы не страна!', ephemeral=True)
            return None

        inv = country.inventory
        options = []
        for name, item in inv.items():
            if int(item.quantity):
                options.append(SelectOption(label=f'{name} - {int(item.quantity)}шт.', value=name))
        
        view = View()
        select = Select(placeholder='Выберите товар', options=options)
        select.callback = lambda interaction: use_callback(interaction, country)
        view.add_item(select)

        await ctx.reply('Что должно испариться?', view= view, ephemeral=True)
        
