from ..library import hybrid_command, has_permissions, describe, Context, deps
from ..library import give_all_countries
from ..library.callbacks import country_selected

class AddCommand:
    @hybrid_command (name= 'add', description='Дать стране новые заводы')
    @has_permissions(administrator= True)
    async def add(self, ctx: Context):
        countries = await give_all_countries()
        
        values = {i: i for i in countries}
        view = deps.ChooseMenu(values, country_selected)
        msg = await ctx.send('Выберите страну', view= view, ephemeral=True)
        view.message = msg