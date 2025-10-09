from ..library.modules import hybrid_command, has_permissions, describe, Context, SelectOption, View, Select, Button
from ..library.functions import give_all_countries
from ..library.callbacks.addCallback import factory_ask, army_ask

class AddCommand:
    @hybrid_command (name= 'add', description='Дать стране новые заводы')
    @has_permissions(administrator= True)
    @describe(page='Выберите страницу')
    async def add(self, ctx: Context, page: int = 1):
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
        #-----------------IF YOU ENDED COMMENT OR DELETE THIS-----------------------------------------------
        select = Select(placeholder= 'Какой стране дать?', options= options)
        select.callback = factory_ask
        view.add_item(select)
        #---------------------------------------------------------------------------------------------------



        #---------------------------AND UNCOMMENT THIS------------------------------------------------------
        # army = Button(label='Армия', emoji='🪖')
        # army.callback = army_ask
        # enterprise = Button(label='Предприятия', emoji='🏭')
        # enterprise.callback = factory_ask

        # view.add_item(army, enterprise)
        #---------------------------------------------------------------------------------------------------
        
        
        if ctx.interaction:
            await ctx.interaction.response.send_message('Пока что выдать можно только фабрики', view= view, ephemeral=True)
        else:
            await ctx.send('Пока что выдать можно только фабрики', view= view)