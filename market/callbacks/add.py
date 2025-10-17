from ..library import Interaction, give_country
from ..modals import AddModal
from ..library.functions import give_items

async def add(interaction: Interaction):
    item = ''.join(interaction.data['values'])
    country = await give_country(interaction.user.mention)
    items_count = await give_items(country, item)

    if not country:
        await interaction.response.edit_message(content='Вы не зарегистрированы!', embed=None)
        return None
    
    modal = AddModal(country, item, items_count)
    await interaction.response.send_modal(modal)