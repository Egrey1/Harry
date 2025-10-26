from ..library.modules import hybrid_command, SelectOption, Select, View, Context, describe
from ..library.functions import give_all_countries
from ..library.callbacks.changenicknamecallback import ChangeNickname

class ChangeNicknameCommand(ChangeNickname):
    @hybrid_command(name= 'change_nickname', description='Меняет никнейм стране')
    @describe(page='Сменить страницу')
    async def change_nickname(self, ctx: Context, page: int = 1):

        countries = await give_all_countries()
        view = View()
        options = []

        PAGE_SIZE = 25
        try:
            options = [SelectOption(label= countries[i], value=countries[i]) for i in range((page - 1) * PAGE_SIZE, min((page) * PAGE_SIZE, len(countries))) if i < len(countries)]
            
            if not options:
                if ctx.interaction:
                    await ctx.interaction.response.send_message('Неправильно введена страница')
                else:
                    await ctx.send('Неправильно введена страница', view= view)
                return None
        except:
            if ctx.interaction:
                await ctx.interaction.response.send_message('Неправильно введена страница')
            else:
                await ctx.send('Неправильно введена страница', view= view)

        select = Select(placeholder= 'Выбрать здесь', options= options)
        

        select.callback = self.change_nickname_callback
        view.add_item(select)

        await ctx.send('Какой стране поменять никнейм',ephemeral=True, view= view)


    
