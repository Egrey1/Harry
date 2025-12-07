from ..modules import (Interaction,  Modal, TextInput,
                       con)

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
            money = await get_money(self.country) # EDIT! USE Country OBJECT AND .balance ATTRIBUTE
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