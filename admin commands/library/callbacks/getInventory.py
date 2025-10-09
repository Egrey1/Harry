from ..modules import Interaction, get_inventory, CURRENCY, Embed

async def getinventory(interaction: Interaction):
    country = interaction.data['values'][0]

    inventory = await get_inventory(country)
    embed_desc = ''

    for name, count in inventory.items():
        if name not in ['name', 'Деньги'] and int(count) > 0:
            embed_desc += f"{name} - {int(count)}\n\n"
    
    embed = Embed(title=f'Баланс страны {country}: {CURRENCY}{inventory['Деньги']}', description=embed_desc)
    await interaction.response.send_message(embed=embed, ephemeral=True)

