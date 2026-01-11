from .modules import Interaction
import dependencies as deps
from .modals.quantity import Quantity
from .modals.use_modal import UseModal


async def give_callback(interaction: Interaction, country_from: deps.Country, country_to: deps.Country):
    item_name = interaction.data['values'][0]
    inv_item = country_from.inventory.get(item_name)
    had = inv_item.quantity if inv_item else 0

    modal = Quantity(item_name, had, country_from, country_to)
    await interaction.response.send_modal(modal)


async def use_callback(interaction: Interaction, country: deps.Country):
    item_name = interaction.data['values'][0]
    modal = UseModal(item_name, country)
    await interaction.response.send_modal(modal)