from ..modules import Interaction, Embed, deps

async def getinventory(interaction: Interaction, value: str):
    country = deps.Country(value)

    inventory = country.inventory
    embed_desc = ''

    for name, item in inventory.items():
        item: deps.Item
        if int(item.quantity):
            embed_desc += f"{name} - {int(item.quantity)}\n\n"
    
    embed = Embed(title=f'Баланс страны {country}: {deps.CURRENCY}{country.balance}', description=embed_desc)
    await interaction.response.send_message(embed=embed, ephemeral=True)

