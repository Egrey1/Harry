from discord import Interaction, SelectOption, Member, app_commands
from discord.ui import Modal, TextInput, View, Select
from discord.ext import commands

from sqlite3 import connect as con
from sqlite3 import Row

from config import CURRENCY, give_country, get_inventory
from config import DATABASE_COUNTRIES as DATABASE_PATH



class Quantity(Modal):
    def __init__(self, item, had, country1, country2):
        # Сохраняем значения внутри класса
        super().__init__(title='Введите количество')
        self.country1 = country1
        self.country2 = country2
        self.item = item

		# Создаем поле для заполнения
        self.quantity = TextInput(label=f'У вас ' + str(had), placeholder='Вы можете передать столько же', required=True)
        self.add_item(self.quantity)
    
    
    async def on_submit(self, interaction: Interaction) -> None:
        # Получаем значение и проверяем его на правильность
        quantity = self.quantity.value
        await interaction.response.defer(ephemeral=True)
        try:
            quantity = int(quantity)
        except:
            interaction.followup.send('Введите целое число!', ephemeral= True)
            return None
        
        # Получаем весь инвентарь страны
        inventory = await get_inventory(self.country1)
        
        # Проверяем, есть ли у страны,котораяпередает, столько предметов
        if inventory[self.item] < quantity:
            interaction.followup.send('У вас нет столько!', ephemeral= True)
            return None
        
        # Проводил SQL запросы
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
        							UPDATE countries_inventory
        							SET "{self.item}" = "{self.item}" - {quantity}
        							WHERE name = "{self.country1}"
        							""")
        connect.commit()
        
        cursor.execute(f"""
        							UPDATE countries_inventory
        							SET "{self.item}" = "{self.item}" + {quantity}
        							WHERE name = "{self.country2}"
        							""")
        connect.commit()
        
        cursor.execute(f"""
        							SELECT "{self.item}"
        							FROM countries_inventory
        							WHERE name = "{self.country1}"
        							""")
        have = cursor.fetchone()[0]
        connect.close()
        
        # Все прошло хорошо
        await interaction.followup.send(f'Теперь у вас: {have}\nА сколько у `{self.country2}` я не знаю, и даже если знал не сказал бы =]', ephemeral= True)
        



class ItemsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def select_callback(self, interaction: Interaction, country1, country2):
        # Получаем предмет и смотрим сколько их у него и сколько он может передать 
        item = ''.join(interaction.data['values']) 
        await interaction.response.defer(ephemeral= True)
        had = await get_inventory(country1) 
        had = had[item]

		# Создаем модальное окно
        modal = Quantity(item, had, country1, country2)
        await interaction.response.send_modal(modal)




    
    @commands.hybrid_command (name= 'give', description='Передать вооружение стране')
    @app_commands.describe(member='Кому передать')
    async def give(self, ctx: commands.Context, member: Member):
        # Получаем названия их стран если они ими являются
        country1 = await give_country(ctx.author.mention)
        country2 = await give_country(member.mention)
        
        # Это слеш команда?
        is_interaction = bool(ctx.interaction)
        interaction = None
        if is_interaction:
            interaction = ctx.interaction
            await interaction.response.defer(ephemeral= True) 

		# Проверяем,являются ли пользователи стрснами 
        if not country1:
            if is_interaction:
                await interaction.followup.send('Вы не страна!', ephemeral= True) 
                return None
            await ctx.send('Вы не страна!')
            return None
        elif not country2:
            if is_interaction:
                await interaction.followup.send('Он не страна!', ephemeral= True) 
                return None
            await ctx.send('Он не страна!')
            return None
        
        # Создаем список предметов 
        inv = await get_inventory(country1)
        options = []
        for name, count in inv.items():
            if name not in ('name', 'Пехота', 'Морпехота', 'Десантник', 'Кавалерия'):
                options.append(SelectOption(label=f'{name} - {count}шт.', value=name))


        # Создаем объект 
        view = View()
        select = Select(placeholder='Выберите товар', options=options)
        select.callback = lambda interaction: self.select_callback(interaction, country1, country2)

		# Отправляем сообщение. Если была введена слеш команда, то отправляем только ему()
        view.add_item(select)
        if is_interaction:
            interaction.followup.send('Выберите что хотите передать, но только тихо....', ephemeral= True, view= view)
        else:
            ctx.send('Выберите что передать', view= view)



    

    

    




async def setup(bot):
    await bot.add_cog(ItemsCog(bot))