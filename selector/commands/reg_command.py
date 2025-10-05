from ..library.modules import (commands, app_commands, 
                       SelectOption, 
                       View, Select,
                       game_state, give_country)

from ..library.callbacks.regCallback import picker_callback

from ..library.functions import give_all_countries



class RegCoommand():
    @commands.hybrid_command(name='reg', description='Зарегистрироваться за страну')
    @app_commands.describe(page='На какую страницу переключить селектор')
    async def send_role_picker(self, ctx: commands.Context, page: int = 1) -> None:
        if not ctx.interaction:
            return None
        
        if await give_country(ctx.interaction.user.mention):
            await ctx.interaction.response.send_message('Чего это? За две страны одновременно поиграть захотелось? А вот нельзя, не разрешаю!')
            return None

        if not game_state['game_started']:
            await ctx.interaction.response.send_message('Дождитесь начала вайпа!', ephemeral= True)
            return None
        countries = await give_all_countries()  

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
        
        view = View()
        select = Select(placeholder='Выберите страну', options=options)
        select.callback = picker_callback

        view.add_item(select)
        
        if ctx.interaction:
            if not options:
                await ctx.interaction.response.send_message("Увы, но доступных для регистрации стран нет", ephemeral= True)
                return None
            await ctx.interaction.response.send_message("Вам представлен список доступных для регистрации стран", view=view, ephemeral=True)