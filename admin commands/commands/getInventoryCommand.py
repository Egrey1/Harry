from ..library.modules import hybrid_command, has_permissions, SelectOption, View, Select, Context, describe
from ..library.functions import give_all_countries
from ..library.callbacks import getinventory

class GetInventoryCommand:

    @hybrid_command(name="getinv", description="Команда для получения инвентаря страны")
    @has_permissions(administrator=True)
    @describe(page='Выберите страницу')
    async def getinventory(self, ctx: Context, page: int = 1):
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
        
        countries = await give_all_countries()
        PAGE_SIZE = 25
        try:
            options = [SelectOption(label= countries[i], value=countries[i]) for i in range((page - 1) * PAGE_SIZE, min((page) * PAGE_SIZE, len(countries))) if i < len(countries)]
            
            if not options:
                if ctx.interaction:
                    await ctx.interaction.response.send_message('Неправильно введена страница или список пуст', ephemeral=True)
                else:
                    await ctx.send('Неправильно введена страница или список пуст')
                return None
        except:
            if ctx.interaction:
                await ctx.interaction.response.send_message('Неправильно введена страница или список пуст', ephemeral=True)
            else:
                await ctx.send('Неправильно введена страница или список пуст')


        view = View()
        select = Select(placeholder='Выберите страну, чтобы получить её инвентарь', options=options)
        select.callback = getinventory
        view.add_item(select)
        if ctx.interaction:
            await ctx.interaction.followup.send('Выберите страну, чтобы получить её инвентарь', view=view, ephemeral=True)
        else:
            await ctx.send('Выберите страну, чтобы получить её инвентарь', view=view)