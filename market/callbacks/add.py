from ..library import Interaction, deps
from ..modals import AddModal

async def add(interaction: Interaction):
    item = ''.join(interaction.data['values'])
    country = deps.Country(interaction.user.mention)

    if not country:
        await interaction.response.edit_message(content='Вы не зарегистрированы!', embed=None)
        return None

    items_count = country.inventory.get(item).quantity if country.inventory.get(item) else 0

    modal = AddModal(country, item, items_count)
    await interaction.response.send_modal(modal)