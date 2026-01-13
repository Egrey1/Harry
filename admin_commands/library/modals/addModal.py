from ..modules import Modal, TextInput, Interaction, con, deps # deps.Item...

class MarketEdit(Modal):
    def __init__(self, item: deps.Item, country: deps.Country):
        
        super().__init__(title=f'Редактирование {item.name}')
        self.item = item
        self.country = country
        
        self.quantity= TextInput(label= 'Сколько добавить', placeholder=f'Текущее количество: {country.market.inventory[item.name].quantity}', required= False)
        self.price= TextInput(label= 'Новая цена', placeholder=f'Текущая цена: {country.market.inventory[item.name].price}', required= False)
        
        self.add_item(self.quantity)
        self.add_item(self.price)
    
    async def on_submit(self, interaction: Interaction) -> None:
        quantity = self.country.market.inventory[self.item.name].quantity + int(self.quantity.value)
        price = int(self.country.market.inventory[self.item.name].price if self.price.value == '' else self.price.value)
        
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
    def __init__(self, item: deps.Item, country: str | deps.Country):
        super().__init__(title="Выбор количества")  
        self.item = item
        self.country_name = country if isinstance(country, str) else getattr(country, 'name')
        
        self.quantity= TextInput(label= 'Выберите количество, совершенно любое', placeholder= 'Столько и будет выдано', required= True)
        self.add_item(self.quantity)

    async def on_submit(self, interaction: Interaction) -> None:
        quantity = int(self.quantity.value) + self.item.quantity # hehe naebal
        
        self.item.edit_quantity(quantity if quantity >= 0 else 0, self.country_name)
        await interaction.response.send_message("Все готово!", ephemeral=True)
        
        
        
        
        