from ..library import hybrid_command, has_permissions, Context, describe, deps
from ..library import give_all_countries
from ..library.callbacks.changenicknamecallback import ChangeNickname

class ChangeNicknameCommand(ChangeNickname):
    @hybrid_command(name= 'change_nickname', description='Меняет никнейм стране')
    @has_permissions(administrator= True)
    async def change_nickname(self, ctx: Context):
        countries = await give_all_countries()

        values = {i: i for i in countries}
        view = deps.ChooseMenu(values, self.change_nickname_callback)
        msg = await ctx.send('Какой стране поменять никнейм', view= view, ephemeral=True)
        view.message = msg