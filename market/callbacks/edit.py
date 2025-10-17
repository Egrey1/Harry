from ..library import Interaction, give_country
from ..library.functions import give_items, country_positions
from ..modals import EditModal

async def edit(interaction: Interaction):
    item = interaction.data['values'][0].split(' - ')[0]

    country = await give_country(interaction.user.mention)
    if not country:
        await interaction.response.send_message("Вы не зарегистрированы!", ephemeral=True)
        return
    
    have = await give_items(country, item)
    on_market = (await country_positions(country))[item]

    modal = EditModal(country, item, have, on_market) 
    await interaction.response.send_modal(modal)