from ..modules import Interaction, SelectOption, View, Select, Button, deps
from ..functions import give_all_factories, give_all_proops
from ..modals.addModal import Quantity, MarketEdit

async def country_selected(interaction: Interaction):
    country = Country(interaction.data['values'][0])
    view = View()
    
    
    army = Button(label='Армия', emoji='🪖')
    army.callback = lambda inter: army_ask(inter, country)
        
    enterprise = Button(label='Предприятия', emoji='🏭')
    enterprise.callback = lambda inter: factory_ask(inter, country)
        
    market = Button(label='Рынок', emoji='📨')
    market.callback = lambda inter: market_ask(inter, country)


    view.add_item(army)
    view.add_item(enterprise)
    view.add_item(market)


    await interaction.response.send_message('Что именно выдать/забрать?', view=view, ephemeral= True)



async def market_ask(interaction: Interaction, country: Country):
    purchasable = country.market.inventory.keys()
    
    view = View()
    
    select = Select(placeholder= 'Выберите предмет', options= [SelectOption(label= i, value= i) for i in purchasable])
    select.callback = lambda inter: market_add(inter, country)
        
    view.add_item(select)
    
    await interaction.response.send_message(f'Страна {country}. Чтобы забрать введите отрицательное число, если нужно забрать все, введите число значительно превышающее существующее. Для добавления ограничений нет', view= view, ephemeral= True)
    
    
    
async def market_add(interaction: Interaction, country: Country):
    item = Item(interaction.data['values'][0])
    
    modal = MarketEdit(item, country)
    await interaction.response.send_modal(modal)



async def army_ask(interaction: Interaction, country: Country):
    view = View()
    
    select = Select(placeholder= 'Выберите Объект', options=[SelectOption(label= i, value= i) for i in (await give_all_proops()) ]) # Select an object
    select.callback = lambda inter: army_add(inter, country)
    
    view.add_item(select)

    await interaction.response.send_message(f'Страна {country}', view= view, ephemeral= True)



async def army_add(interaction: Interaction, country: Country):
    item = Item(interaction.data['values'][0]) # soldier 

    modal = Quantity(item, country)
    await interaction.response.send_modal(modal)



async def factory_ask(interaction: Interaction, country: Country):    
    factories = await give_all_factories()
    options = []
    
    for factory in factories:
        options.append(SelectOption(label= factory['name'], value= factory['name']))
    
    view = View()
    select = Select(placeholder= 'Выберите фабрику', options= options)
    select.callback = factory_add
    view.add_item(select)
    
    await interaction.response.send_message(f'Страна `{country}`', view= view, ephemeral=True)



async def factory_add(interaction: Interaction):
    item = Factory(interaction.data['values'][0])
    country = await give_country(interaction.user.mention)

    # Создаем модальное окно
    modal = Quantity(item, country)
    await interaction.response.send_modal(modal)