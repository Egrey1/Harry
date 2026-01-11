from ..library.modules import hybrid_command, has_permissions, describe, Context, SelectOption, View, Select, deps
from ..library.functions import give_all_surrend_countries
from ..library.callbacks import no_surrend_callback

class NoSurrendCommand:
    @hybrid_command(name='nosurrend', description='Снять метку капитуляции')
    @has_permissions(administrator= True)
    async def nosurrend(self, ctx: Context):
        countries = await give_all_surrend_countries()
        
        values = {i: i for i in countries}
        view = deps.ChooseMenu(values, no_surrend_callback)
        msg = await ctx.send('Введите страну, которая больше не отмечена как сдавшиеся', view= view, ephemeral=True)
        view.message = msg