from ..library import hybrid_command, has_permissions, SelectOption, View, Select, Context, describe, deps
from ..library import give_all_countries
from ..library.callbacks import getinventory

class GetInventoryCommand:
    @hybrid_command(name="getinv", description="Команда для получения инвентаря страны")
    @has_permissions(administrator=True)
    async def getinventory(self, ctx: Context):
        countries = await give_all_countries()

        values = {i: i for i in countries}
        view = deps.ChooseMenu(values, getinventory)
        msg = await ctx.send('Выберите страну, чтобы получить её инвентарь', view= view, ephemeral=True)
        view.message = msg