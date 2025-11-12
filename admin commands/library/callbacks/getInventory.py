from ..modules import Interaction, get_inventory, CURRENCY, Embed, Country, Item

async def getinventory(interaction: Interaction):
    country = Country(interaction.data['values'][0])

    inventory = country.inventory
    embed_desc = ''

    for name, item in inventory.items():
        item: Item
        if int(item.quantity):
            embed_desc += f"{name} - {int(item.quantity)}\n\n"
    
    embed = Embed(title=f'Баланс страны {country}: {CURRENCY}{country.balance}', description=embed_desc)
    await interaction.response.send_message(embed=embed, ephemeral=True)

