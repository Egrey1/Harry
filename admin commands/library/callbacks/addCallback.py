from ..modules import Interaction, SelectOption, View, Select
from ..functions import give_all_factories
from ..modals.addModal import Quantity

async def factory_ask(interaction: Interaction):
    await interaction.response.defer(ephemeral=True) #added "await" here
    country = ''.join(interaction.data['values'])
    print(country)
    
    factories = await give_all_factories()
    options = []
    
    for factory in factories:
        options.append(SelectOption(label= factory['name'], value= factory['name']))
        print(factory['name'])
    
    view = View()
    select = Select(placeholder= 'Выберите фабрику', options= options)
    select.callback = lambda interaction: select_callback(interaction, country)
    view.add_item(select)
    
    await interaction.response.send_message(f'Страна `{country}`', view= view, ephemeral='True')
    #await interaction.response.defer(ephemeral=True)

async def select_callback(interaction: Interaction, country):
    # Получаем название страны 
    item = ''.join(interaction.data['values'])

    # Создаем модальное окно
    modal = Quantity(item, country)
    await interaction.response.send_modal(modal)