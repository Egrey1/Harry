from ..modules import Interaction, SelectOption, View, Select, give_country, Button
from ..functions import give_all_factories, give_all_proops
from ..modals.addModal import Quantity

async def country_selected(interaction: Interaction):
    country = interaction.data['values'][0]
    view = View()
    army = Button(label='Армия', emoji='🪖')
    army.callback = lambda inter: army_ask(inter, country)
    enterprise = Button(label='Предприятия', emoji='🏭')
    enterprise.callback = lambda inter: factory_ask(inter, country)

    view.add_item(army)
    view.add_item(enterprise)

    await interaction.response.send_message('Что именно выдать?', view=view, ephemeral= True)

async def army_ask(interaction: Interaction, country: str):
    # Your code here
    # I don't exactly get how this is supposed to work
    #country = ''.join(interaction.data['values'])
    #army = await give_country(interaction.user.mention)
    
    view = View()
    select = Select(placeholder= 'Выберите Объект', options=[SelectOption(label= i, value= i) for i in (await give_all_proops()) ]) # Select an object
    select.callback = lambda inter: army_add(inter, country)
    view.add_item(select)

    await interaction.response.send_message(f'Страна {country}', view= view, ephemeral= True)

async def army_add(interaction: Interaction, country: str):
    item = interaction.data['values'][0] # soldier
    itemType = 'army'

    modal = Quantity(item, country, itemType)
    await interaction.response.send_modal(modal)

async def factory_ask(interaction: Interaction, country: str):    
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
    # Получаем название страны 
    item = ''.join(interaction.data['values'])
    country = await give_country(interaction.user.mention)
    itemType = 'factory'

    # Создаем модальное окно
    modal = Quantity(item, country, itemType)
    await interaction.response.send_modal(modal)