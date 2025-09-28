from discord import Interaction, SelectOption, Member, app_commands
from discord.ui import Modal, TextInput, View, Select
from discord.ext import commands

from sqlite3 import connect as con
from sqlite3 import Row

from config import DATABASE_COUNTRIES as DATABASE_PATH
from config import DATABASE_ROLE_PICKER as ROLE_PICKER_PATH



class Quantity(Modal):
    def __init__(self, item, country):
        super().__init__(title="Выбор количества")  
        self.item = item
        self.country = country
        
        self.quantity= TextInput(label= 'Выберите количество, совершенно любое', placeholder= 'Будет выдано столько фабрик', required= True)
        self.add_item(self.quantity)

    async def on_submit(self, interaction: Interaction) -> None:
        quantity = self.quantity.value
        
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        
        cursor.execute(f"""
                        UPDATE country_factories
                        SET '{self.item}' = {quantity} + '{self.item}'
                        WHERE name = '{self.country}'
                        """)
        connect.commit()
        connect.close()
        
        await interaction.response.send_message("Все готово!", ephemeral=True)
        



class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def give_all_factories(self) -> tuple:
        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute("""
                    SELECT name, cost, `desc`
                    FROM factories
                    """)
        a = cursor.fetchall()
        connect.close()
        result = []

        for i in a:
            result.append(dict(i))
        
        return tuple(result)

    async def select_callback(self, interaction: Interaction, country):
        # Получаем название страны 
        item = ''.join(interaction.data['values'])

        # Создаем модальное окно
        modal = Quantity(item, country)
        await interaction.response.send_modal(modal)

    async def factory_ask(self, interaction: Interaction):
        interaction.response.defer(ephemeral=True)
        country = ''.join(interaction.data['values'])
        print(country)
        
        factories = await self.give_all_factories()
        options = []
        
        for factory in factories:
            options.append(SelectOption(label= factory['name'], value= factory['name']))
            print(factory['name'])
        
        view = View()
        select = Select(placeholder= 'Выберите фабрику', options= options)
        select.callback = lambda interaction: self.select_callback(interaction, country)
        view.add_item(select)
        
        await interaction.response.send_message(f'Страна `{country}`', view= view, ephemeral='True')


    async def give_all_countries(self) -> tuple:
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT name
                        FROM roles
                        """)
        result = tuple([row[0] for row in cursor.fetchall()])  
        connect.close()
        return result
    
    async def give_all_non_surrend_countries(self) -> tuple:
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT name
                        FROM roles
                        WHERE surrender IS NOT NULL
                        """)
        result = tuple([row[0] for row in cursor.fetchall()])  
        connect.close()
        return result
    
    async def give_all_surrend_countries(self) -> tuple:
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT name
                        FROM roles
                        WHERE surrender IS NULL
                        """)
        result = tuple([row[0] for row in cursor.fetchall()])  
        connect.close()
        return result
    
    @commands.hybrid_command (name= 'add', description='Дать стране новые заводы')
    @commands.has_permissions(administrator= True)
    @app_commands.describe(page='Выберите страницу')
    async def add(self, ctx: commands.Context, page: int = 1):
        countries = await self.give_all_countries()
        
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
        select = Select(placeholder= 'Какой стране дать?', options= options)
        select.callback = self.factory_ask
        view.add_item(select)
        
        if ctx.interaction:
            await ctx.interaction.response.send_message('Пока что выдать можно только фабрики', view= view, ephemeral=True)
        else:
            await ctx.send('Пока что выдать можно только фабрики', view= view)
    
    async def surrend_callback(self, interaction: Interaction):
        country = ''.join(interaction.data['values'])
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                       UPDATE roles
                       SET surrender = ' '
                       WHERE name = '{country}'
                       """)
        connect.commit()

        interaction.response.send_message('Страна подписана как сдавшиеся!')
    
    async def no_surrend_callback(self, interaction: Interaction):
        country = ''.join(interaction.data['values'])
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                       UPDATE roles
                       SET surrender = NULL
                       WHERE name = '{country}'
                       """)
        connect.commit()

        interaction.response.send_message('Страна подписана как сдавшиеся!')

    @commands.hybrid_command(name='surrend', description='Объявить о капитуляции для страны')
    @commands.has_permissions(administrator= True)
    @app_commands.describe(page='Выберите страницу')
    async def surrend(self, ctx: commands.Context, page: int = 1):
        countries = await self.give_all_non_surrend_countries()
        
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
        select = Select(placeholder= 'Кто этот лох?', options= options)
        select.callback = self.surrend_callback
        view.add_item(select)
        
        if ctx.interaction:
            await ctx.interaction.response.send_message('Введите какая страна сдалась', view= view, ephemeral=True)
        else:
            await ctx.send('Введите какая страна сдалась', view= view)
    
    @commands.hybrid_command(name='surrend', description='Объявить о капитуляции для страны')
    @commands.has_permissions(administrator= True)
    @app_commands.describe(page='Выберите страницу')
    async def surrend(self, ctx: commands.Context, page: int = 1):
        countries = await self.give_all_surrend_countries()
        
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
        select = Select(placeholder= 'Опять кто-то из пепла восстает?', options= options)
        select.callback = self.no_surrend_callback
        view.add_item(select)
        
        if ctx.interaction:
            await ctx.interaction.response.send_message('Введите страну, которая больше не отмечена как сдавшиеся', view= view, ephemeral=True)
        else:
            await ctx.send('Введите страну, которая больше не отмечена как сдавшиеся', view= view)




    

    

    


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
