from ..library import Interaction, give_country
from ..modals import EditModal

async def edit(interaction: Interaction):
    item = interaction.data['values'][0].split(' - ')[0]

    country = await give_country(interaction.user.mention)
    if not country:
        await interaction.response.send_message("Вы не зарегистрированы!", ephemeral=True)
        return
    
    have_item = country.inventory.get(item)
    have = have_item.quantity if have_item else 0
    market_item = country.market.inventory.get(item)
    on_market = f"{market_item.quantity} {market_item.price}" if market_item else "0 0"

    modal = EditModal(country, item, have, on_market) 
    await interaction.response.send_modal(modal)