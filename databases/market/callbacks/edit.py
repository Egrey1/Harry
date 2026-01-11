from ..library import Interaction, deps
from ..modals import EditModal

async def edit(interaction: Interaction):
    item = interaction.data['values'][0].split(' - ')[0]

    country = deps.Country(interaction.user.mention)
    if not country.busy:
        await interaction.response.send_message("Вы не зарегистрированы!", ephemeral=True)
        return
    
    have_item = country.inventory.get(item)
    have = have_item.quantity if have_item else 0
    market_item = country.market.inventory.get(item)
    on_market = f"{market_item.quantity} {market_item.price}" if market_item else "0 0"

    modal = EditModal(country, item, have, on_market) 
    await interaction.response.send_modal(modal)