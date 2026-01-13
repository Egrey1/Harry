from ..library import Interaction, Select, SelectOption, View, deps
from ..modals import BuyModal

async def choosed_seller(interaction: Interaction, country: deps.Country, item_name: str, positions: dict[str, dict]):
    seller_country = interaction.data['values'][0]
    if seller_country == country.name:
        await interaction.response.send_message(f'Ты чего, не в себе что ли? Нельзя у себя покупать!', ephemeral=True)
        return
    
    modal = BuyModal(country, item_name, seller_country, positions)
    await interaction.response.send_modal(modal)



async def buy(interaction: Interaction, country: deps.Country, positions: dict[str, dict]):
    item_name = interaction.data['values'][0].split(' - ')[0]
    sellers = positions[item_name]['sellers']

    view = View()
    options = []
    for seller in sellers:
        options.append(SelectOption(label=f"{seller['country']} - {deps.CURRENCY}{seller['price']}", value=seller['country']))
    select = Select(placeholder='Выберите продавца', options=options)
    select.callback = lambda interaction: choosed_seller(interaction, country, item_name, positions)

    view.add_item(select)
    await interaction.response.send_message(f'Выберите продавца для покупки {item_name}:', view=view, ephemeral=True)
