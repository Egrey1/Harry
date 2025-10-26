from ..modules import Modal, TextInput, Interaction, con, DATABASE_PATH, Item, Country

class MarketEdit(Modal):
    def __init__(self, item: Item, country: Country):
        
        super().__init__(title='Выберите количество и новую цену в рынке для предмета')
        self.item = item
        self.country = country
        
        self.quantity= TextInput(label= 'Сколько добавить', placeholder=f'Текущее количество: {country.market.inventory[item].quantity}', required= False)
        self.price= TextInput(label= 'Новая цена', placeholder=f'Текущая цена: {country.market.inventory[item].price}', required= False)
        
        self.add_item(self.quantity)
        self.add_item(self.price)
    
    async def on_sumbit(self, interaction: Interaction) -> None:
        quantity = self.country.market.inventory[self.item].quantity + int(self.quantity.value)
        price = self.price.value
        
        if quantity < 0:
            quantity = 0
        if price < 0:
            interaction.response.send_message('Изменить баланас ты и по-другому можешь, а цену поставить ниже нуля нельзя!', ephemeral= True)
            return None
        
        if not self.quantity.value and not self.price.value:
            interaction.response.send_message('Скажи честно, ты не в себе?', ephemeral=True)
        
        self.item.quantity = quantity
        self.item.price = price
        
        self.country.market.edit_item(self.item)
        
        interaction.response.send_message(f'Команда выполнена успешо! {self.country} Теперь продает {self.item.name} за {self.country.market.inventory[self.item.name].price}')
        return None

class Quantity(Modal):
    def __init__(self, item: Item, country: str | Country):
        super().__init__(title="Выбор количества")  
        self.item = item
        self.country = country
        self.itemType = itemType
        
        self.quantity= TextInput(label= 'Выберите количество, совершенно любое', placeholder= 'Столько и будет выдано', required= True)
        self.add_item(self.quantity)

    async def on_submit(self, interaction: Interaction) -> None:
        quantity = int(self.quantity.value) + item.quantity # hehe naebal
        
        item.edit_quantity(quantity if quantity >= 0 else 0, country)
        await interaction.response.send_message("Все готово!", ephemeral=True)
        
        
        
        
        