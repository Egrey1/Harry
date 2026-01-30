from ..library import hybrid_command, Context, deps, SelectOption, Select, View, Interaction
from ..modals import RemFactModal

async def remove_factories_callback(interaction: Interaction, country: deps.Country) -> None:
    factory = deps.Factory(interaction.data['values'][0], country=country)
    if factory.quantity <= 0:
        await interaction.response.send_message('У вас нет таких фабрик для разрушения!', ephemeral=True)
        return
    
    modal = RemFactModal(factory)
    await interaction.response.send_modal(modal)

class RemFactCommand:
    @hybrid_command(name='removef', description='Разрушить свои фабрики для освобождения строительных ячеек')
    async def remove_factories(self, ctx: Context):
        country = deps.Country(ctx.author.mention)
        
        if not country.busy:
            await ctx.reply('Вы не страна!', ephemeral=True)
            return
        
        options = []
        for factory in country.factories.values():
            if factory.quantity > 0:
                options.append(
                    SelectOption(label=f"{factory.name} ({factory.quantity})", value=factory.name)
                    )
        if not options:
            await ctx.reply('У вас нет фабрик для разрушения!', ephemeral=True)
            return
        
        view = View()
        select = Select(placeholder='Выберите фабрику для разрушения', options=options)
        select.callback = lambda inter: remove_factories_callback(inter, country)
        view.add_item(select)

        await ctx.reply('Выберите фабрику для разрушения:', view=view, ephemeral=True)