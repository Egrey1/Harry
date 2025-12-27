from ..modules import (Interaction,  Modal, TextInput,
                       con, deps)

# Модальное окно для запроса количества
class Buy(Modal):
    def __init__(self, money: int, cost: int, country: deps.Country, factory: deps.Factory):
        super().__init__(title='Введите количество')
        self.cost = cost
        self.max_buy = int(money / cost) if cost != 0 else '∞'
        self.country = country
        self.factory = factory

        self.quantity = TextInput(label=f'У вас ' + deps.CURRENCY + str(money), placeholder='Вы можете приобрести ' + str(self.max_buy) + 'шт.', required=True)
        self.add_item(self.quantity)
    
    async def on_submit(self, interaction: Interaction) -> None:
        # Делаем проверку на значение
        quantity = self.quantity.value
        await interaction.response.defer(ephemeral=True)
        self.country = deps.Country(self.country.name)  # Обновляем данные страны
        try:
            quantity = int(quantity)
            
            # Проверяем может ли человек позволить себе этот предмет
            money = self.country.balance 
            if money < quantity * self.cost:
                await interaction.followup.send('У твоей страны нет столько денег', ephemeral=True)
                return None
            if quantity < 0:
                await interaction.followup.send('Самый хитрый думаешь?', ephemeral=True)
                return None
            
            # Делаем SQL запросы
            connect = con(deps.DATABASE_COUNTRIES_PATH)
            cursor = connect.cursor()
            cursor.execute(f"""
                            UPDATE country_factories
                            SET "{self.factory.name}" = "{self.factory.name}" + {quantity}
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
                            SELECT "{self.factory.name}"
                            FROM country_factories
                            WHERE name = '{self.country}'
                           """)
            count = cursor.fetchone()[0]

            money = self.country.balance
            connect.close()
 
            await interaction.followup.send(f'Теперь у вас {count} зданий вида: {self.factory.name}\nИ {deps.CURRENCY}{money} на балансе', ephemeral=True)
            


        except ValueError:
            await interaction.followup.send('Надо ввести целое число!', ephemeral=True)
            return None