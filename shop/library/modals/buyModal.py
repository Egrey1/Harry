from ..modules import (Interaction,  Modal, TextInput,
                       con, deps)

# Модальное окно для запроса количества
class Buy(Modal):
    def __init__(self, money: int, cost: int, country: deps.Country, factory: deps.Factory):
        super().__init__(title='Введите количество')
        self.cost = cost
        
        # Вычисляем максимум, который можно купить по деньгам
        max_by_money = int(money / cost) if cost != 0 else float('inf')
        
        # Вычисляем максимум, который можно купить по строительным ячейкам
        available_slots = country.get_available_building_slots()
        max_by_slots = (available_slots if available_slots > 0 else 0) if factory.name != 'Коммерческая зона' else max_by_money # ВРЕМЕННО! НАДО ИСПРАВИТЬ!
        
        # Берём минимум из двух ограничений
        self.max_buy = min(max_by_money, max_by_slots) if max_by_money != float('inf') else max_by_slots
        self.max_buy = int(self.max_buy) if self.max_buy != float('inf') else '∞'
        
        self.country = country
        self.factory = factory

        # Обновляем текст с информацией о доступных местах
        slots_info = f' (Доступно ячеек: {available_slots}/{country.building_slots})'
        self.quantity = TextInput(
            label=f'У вас ' + deps.CURRENCY + str(money) + slots_info, 
            placeholder='Вы можете приобрести ' + str(self.max_buy) + ' шт.', 
            required=True
        )
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
            
            # Проверяем, есть ли достаточно строительных ячеек
            available_slots = self.country.get_available_building_slots() if self.factory.name != 'Коммерческая зона' else float('inf')  # ВРЕМЕННО! НАДО ИСПРАВИТЬ!
            if quantity > available_slots:
                await interaction.followup.send(f'Недостаточно строительных ячеек! Доступно: {available_slots}, требуется: {quantity}', ephemeral=True)
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

            money = deps.Country(self.country.name).balance
            connect.close()
 
            await interaction.followup.send(f'Теперь у вас {count} зданий вида: {self.factory.name}\nИ {deps.CURRENCY}{money} на балансе', ephemeral=True)
            


        except ValueError:
            await interaction.followup.send('Надо ввести целое число!', ephemeral=True)
            return None