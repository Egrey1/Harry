from ..modules import Modal, TextInput, Interaction, get_inventory, con, DATABASE_PATH

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