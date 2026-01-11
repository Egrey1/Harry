from ..library.modules import hybrid_command, has_permissions, describe, Context, SelectOption, View, Select, deps
from ..library.functions import give_all_no_surrend_countries
from ..library.callbacks import surrend_callback

class SurrendCommand:
    @hybrid_command(name='surrend', description='Объявить о капитуляции для страны')
    @has_permissions(administrator= True)
    async def surrend(self, ctx: Context):
        countries = await give_all_no_surrend_countries()

        values = {i: i for i in countries}
        vies = deps.ChooseMenu(values, surrend_callback)
        msg = await ctx.send('Введите какая страна сдалась', view= vies, ephemeral=True)
        vies.message = msg