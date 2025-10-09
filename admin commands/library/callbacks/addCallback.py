from ..modules import Interaction, SelectOption, View, Select, give_country
from ..functions import give_all_factories
from ..modals.addModal import Quantity

async def army_ask(interaction: Interaction):
    # Your code here
    # I don't exactly get how this is supposed to work
    #country = ''.join(interaction.data['values'])
    #army = await give_country(interaction.user.mention)
    
    pass

async def army_add(interaction: Interaction):
    item = interaction.data['values'][0] # soldier
    country = await give_country(interaction.user.mention) # Germany
    itemType = 'army'

    modal = Quantity(item, country, itemType)
    await interaction.response.send_modal(modal)

async def factory_ask(interaction: Interaction):
    # don't use it. My mistake
    # await interaction.response.defer(ephemeral=True) #added "await" here
    country = ''.join(interaction.data['values'])
    
    factories = await give_all_factories()
    options = []
    
    for factory in factories:
        options.append(SelectOption(label= factory['name'], value= factory['name']))
    
    view = View()
    select = Select(placeholder= 'Выберите фабрику', options= options)
    select.callback = factory_add
    view.add_item(select)
    
    # only this
    await interaction.response.send_message(f'Страна `{country}`', view= view, ephemeral=True)

async def factory_add(interaction: Interaction):
    # Получаем название страны 
    item = ''.join(interaction.data['values'])
    country = await give_country(interaction.user.mention)
    itemType = 'factory'

    # Создаем модальное окно
    modal = Quantity(item, country, itemType)
    await interaction.response.send_modal(modal)