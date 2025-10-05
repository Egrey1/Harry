from ..modules import Interaction, get_inventory
from ..modals.quantity import Quantity

async def select_callback(self, interaction: Interaction, country1, country2):
    # Получаем предмет и смотрим сколько их у него и сколько он может передать 
    item = ''.join(interaction.data['values'])
    had = await get_inventory(country1) 
    had = had[item]

    # Создаем модальное окно
    modal = Quantity(item, had, country1, country2)
    await interaction.response.send_modal(modal)