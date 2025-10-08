from ..modules import Interaction, get_inventory, CURRENCY

async def getinventory(interaction: Interaction):
    country = interaction.data['values'][0]

    inventory = await get_inventory(country)
    mes = f"Баланс {CURRENCY}{inventory['Деньги']}\n\n"

    for name, count in inventory.items():
        if name not in ['name', 'Деньги'] and int(count) > 0:
            mes += f"{name}: {count}\n"
    
    await interaction.response.send_message(mes, ephemeral=True)

