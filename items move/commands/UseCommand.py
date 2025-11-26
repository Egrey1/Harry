from .library.modules import (hybrid_command, Context, View, Select, SelectOption,
                               give_country, get_inventory)
from .library.callbacks import use_callback

class UseCommand:
    @hybrid_command(name='use', description='Убрать предмет')
    async def use(self, ctx: Context) -> None:
        country = await give_country(ctx.author.mention)
        if not country:
            await ctx.reply('Вы не страна!', ephemeral=True)
            return None

        inv = await get_inventory(country)
        options = []
        for name, count in inv.items():
            if name not in ('name') and int(count):
                options.append(SelectOption(label=f'{name} - {int(count)}шт.', value=name))
        
        view = View()
        select = Select(placeholder='Выберите товар', options=options)
        select.callback = lambda interaction: use_callback(interaction, country)
        view.add_item(select)

        await ctx.reply('Что должно испариться?', view= view, ephemeral=True)
        
