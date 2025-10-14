from ..library.modules import hybrid_command, has_permissions, describe, Context, SelectOption, View, Select
from ..library.functions import give_all_no_surrend_countries
from ..library.callbacks import surrend_callback

class SurrendCommand:
    @hybrid_command(name='surrend', description='Объявить о капитуляции для страны')
    @has_permissions(administrator= True)
    @describe(page='Выберите страницу')
    async def surrend(self, ctx: Context, page: int = 1):
        countries = await give_all_no_surrend_countries()
        
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
        select = Select(placeholder= 'Кто этот лох?', options= options)
        select.callback = surrend_callback
        view.add_item(select)
        
        if ctx.interaction:
            await ctx.interaction.response.send_message('Введите какая страна сдалась', view= view, ephemeral=True)
        else:
            await ctx.send('Введите какая страна сдалась', view= view)