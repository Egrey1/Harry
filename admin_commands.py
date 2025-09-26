from discord import Interaction, SelectOption, Member, app_commands
from discord.ui import Modal, TextInput, View, Select
from discord.ext import commands

from sqlite3 import connect as con

from config import give_country, get_inventory, game_state
from config import DATABASE_COUNTRIES as DATABASE_PATH



class Quantity(Modal):
    def __init__(self, item, country):
    	self.item = item
    	self.country = country
    	
    	self.quantity= TextInput(label= 'Выберите количество, совершенно любое', required= True)
    	self.add_item(self.quantity)
    
    async def on_submit(self, interaction: Interaction) -> None:
        quantity = self.quantity.value
        
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        
        cursor.execute(f"""
        							UPDATE country_factories
        							SET {self.item} = {quantity} + {self.item}
        							WHERE name = {self.country}
        							""")
        connect.commit()
        connect.close()
        
        interaction.response.send_message("Все готово!")
        



class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

	async def give_all_factories(self) -> tuple:
        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute("""
                    SELECT name, cost, desc
                    FROM factories
                    """)
        result = cursor.fetchall()
        connect.close()
        return tuple(result)

	async def select_callback(self, country):
		# Получаем название страны 
        item = ''.join(interaction.data['values'])

		# Создаем модальное окно
        modal = Quantity(item, item, country)
        await interaction.response.send_modal(modal)

    async def factory_ask(self, interaction: Interaction):
        country = ''.join(interaction.data['values'])
        
        factories = give_all_factories()
        options = []
        
        for factory in factories:
        	options.append(SelectOption(label= factory, value= factory))
        
        view = View()
        select = Select(placeholder= 'Выберите фабрику', options= options)
		select.callback = lambda interaction: self.select_callback(interaction, country)
		
		interaction.response.send_message(f'Страна `{country}`', view= view)


	async def give_all_countries(self) -> tuple:
		connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT name
                        FROM roles
                        """)
        result = tuple([row[0] for row in cursor.fetchall()])  
        connect.close()
        return result
    
    @commands.hybrid_command (name= 'add', description='Дать стране новые заводы')
    @app_commands.had_permissions(administrator= True)
    async def add(self, ctx: commands.Context):
    	if ctx.interaction:
    		ctx.interaction.response.deffer(ephemeral= True)
    	countries = await self.give_all_countries()
    	
    	options = []
    	for country in countries:
    		options.append(SelectOption(label= country, value= country))
    	
    	view = View()
    	select = Select(placeholder= 'Какой стране дать?', options= options)
    	select.callback = select_callback
    	view.add_item(select)
    	
    	if ctx.interaction:
    		ctx.interaction.response.send_message('Пока что выдать можно только фабрики', view= view)

    

    

    


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
