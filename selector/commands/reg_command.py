from ..library.modules import (commands, app_commands, 
                       SelectOption, 
                       View, Select,
                       deps)

from ..library.callbacks.regCallback import picker_callback

from ..library.functions import give_all_countries, can_register



class RegCoommand():
    @commands.hybrid_command(name='reg', description='Зарегистрироваться за страну')
    async def send_role_picker(self, ctx: commands.Context) -> None:
        if not ctx.interaction:
            return None
        
        if deps.Country(ctx.author.mention).busy:
            await ctx.interaction.response.send_message('Чего это? За две страны одновременно поиграть захотелось? А вот нельзя, не разрешаю!', ephemeral=True)
            return None
        
        if not can_register(ctx.author) and not ctx.author.resolved_permissions.administrator:
            await ctx.interaction.response.send_message('Подожди день, прежде чем ты сможешь снова зарегистрироваться')

        if not deps.game_state['game_started']:
            await ctx.interaction.response.send_message('Дождитесь начала вайпа!', ephemeral= True)
            return None
        countries = await give_all_countries()  

        values = {i: i for i in countries if not deps.Country(i).busy}
        if not values:
            await ctx.interaction.response.send_message("Увы, но доступных для регистрации стран нет", ephemeral= True)
            return None
        
        view = deps.ChooseMenu(values, picker_callback)
        msg = await ctx.send("Вам представлен список доступных для регистрации стран", view=view, ephemeral=True)
        view.message = msg