from discord import Embed, Interaction, SelectOption
from discord.ui import Modal, TextInput, View, Select
from discord.ext import commands

from sqlite3 import connect as con
from sqlite3 import Row

from config import CURRENCY, give_country, get_cost, get_money
from config import DATABASE_COUNTRIES as DATABASE_PATH


# Модальное окно для запроса количества
class Buy(Modal):
    def __init__(self, money, cost, country, item):
        super().__init__(title='Введите количество')
        self.cost = cost
        self.max_buy = int(money / cost) if cost != 0 else '∞'
        self.country = country
        self.item = item

        self.quantity = TextInput(label=f'У вас ' + CURRENCY + str(money), placeholder='Вы можете приобрести ' + str(self.max_buy) + 'шт.', required=True)
        self.add_item(self.quantity)
    
    async def on_submit(self, interaction: Interaction) -> None:
        # Делаем проверку на значение
        quantity = self.quantity.value
        await interaction.response.defer(ephemeral=True)
        try:
            quantity = int(quantity)
            
            # Проверяем может ли человек позволить себе этот предмет
            money = await get_money(self.country)
            if money < quantity * self.cost:
                await interaction.followup.send('У твоей страны нет столько денег', ephemeral=True)
                return None
            if quantity < 0:
                await interaction.followup.send('Самый хитрый думаешь?', ephemeral=True)
                return None
            
            # Делаем SQL запросы
            connect = con(DATABASE_PATH)
            cursor = connect.cursor()
            cursor.execute(f"""
                            UPDATE country_factories
                            SET "{self.item}" = "{self.item}" + {quantity}
                            WHERE name = "{self.country}"
                           """)
            connect.commit()

            cursor.execute(f"""
                            UPDATE countries_inventory
                            SET "Деньги" = "Деньги" - {int(quantity * self.cost)}
                            WHERE name = "{self.country}"
                           """)
            connect.commit()

            cursor.execute(f"""
                            SELECT "{self.item}"
                            FROM country_factories
                            WHERE name = '{self.country}'
                           """)
            count = cursor.fetchone()[0]

            money = await get_money(self.country)
            connect.close()
 
            await interaction.followup.send(f'Теперь у вас {count} зданий вида: {self.item}\nИ {CURRENCY}{money} на балансе', ephemeral=True)
            


        except ValueError:
            await interaction.followup.send('Надо ввести целое число!', ephemeral=True)
            return None



class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Получаем все фабрики
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

    @commands.hybrid_command()
    async def shop(self, ctx: commands.Context) -> None:
        factories = await self.give_all_factories()
        embed_desc = ''

		# Добавляем все фабрики вместе с ценой и описанием
        for factory in factories:
            embed_desc += '### ' + factory[0] + ' - '+ CURRENCY + str(factory[1]) + '\n```' + factory[2] + '``` \n\n\n'
        
        embed = Embed(title='Все предприятия на продажу: ', description=embed_desc)

		# Выводим
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed)
            return None
        await ctx.send(embed=embed)

    async def buy_callback(self, interaction: Interaction) -> None:
        # Проверяем является ли пользлватель страной
        item = ''.join(interaction.data['values']) 
        country = await give_country(interaction.user.mention)

        if not country :
            await interaction.followup.send('Вы не зарегистрированы!', ephemeral=True)
            return None
        
        # Если да спрашиваем сколько он хочет купить 
        modal = Buy(await get_money(country), await get_cost(item), country, item)
        await interaction.response.send_modal(modal)


    @commands.hybrid_command()
    async def buy(self, ctx: commands.Context):
        options = []

        # Добавляем в список все фабрики
        for factory in await self.give_all_factories():
            options.append(SelectOption(label=factory[0] + ' - ' + CURRENCY + str(factory[1]), value=factory[0]))
        
        # Создаем объект View 
        view = View()
        select = Select(placeholder='Выберите предмет для покупки', options=options)
        select.callback = self.buy_callback
        view.add_item(select)

        if ctx.interaction:
            await ctx.interaction.response.send_message('Здесь вы можете купить что угодно, но только тс-с-с, никто не должен знать', view= view, ephemeral= True)
        else:
            await ctx.send('Здесь вы можете купить что угодно', view=view)




async def setup(bot):
    await bot.add_cog(ShopCog(bot))