from ..modules import Modal, TextInput, Interaction, con, DATABASE_PATH

class Quantity(Modal):
    def __init__(self, item, country, itemType):
        super().__init__(title="Выбор количества")  
        self.item = item
        self.country = country
        self.itemType = itemType
        
        self.quantity= TextInput(label= 'Выберите количество, совершенно любое', placeholder= 'Будет выдано столько фабрик', required= True)
        self.add_item(self.quantity)

    async def on_submit(self, interaction: Interaction) -> None:
        quantity = self.quantity.value
        
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        
        cursor.execute(f"""
                        UPDATE {'country_factories' if self.itemType == 'factory' else 'countries_inventory'}
                        SET {self.item} = {quantity} + {self.item}
                        WHERE name = '{self.country}'
                        """)
        connect.commit()
        connect.close()
        
        await interaction.response.send_message("Все готово!", ephemeral=True)