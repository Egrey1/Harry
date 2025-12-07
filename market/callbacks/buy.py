from ..library import Interaction, Select, SelectOption, View, deps
from ..modals import BuyModal

async def choosed_seller(interaction: Interaction, country: str, item: str, positions: dict[str, dict]):
    seller_country = interaction.data['values'][0]
    if seller_country == country:
        await interaction.response.send_message(f'Ты чего, не в себе что ли? Нельзя у себя покупать!', ephemeral=True)
        return
    
    modal = BuyModal(country, item, seller_country, positions)
    await interaction.response.send_modal(modal)



async def buy(interaction: Interaction, country: str, positions: dict[str, dict]):
    item = interaction.data['values'][0].split(' - ')[0]
    sellers = positions[item]['sellers']

    view = View()
    options = []
    for seller in sellers:
        options.append(SelectOption(label=f"{seller['country']} - {CURRENCY}{seller['price']}", value=seller['country']))
    select = Select(placeholder='Выберите продавца', options=options)
    select.callback = lambda interaction: choosed_seller(interaction, country, item, positions)

    view.add_item(select)
    await interaction.response.send_message(f'Выберите продавца для покупки {item}:', view=view, ephemeral=True)
