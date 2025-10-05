from .modules import (con, DATABASE_COUNTRIES_PATH, DATABASE_ROLE_PICKER_PATH, 
                      Row, Interaction, Embed,
                      give_country, CURRENCY, get_money)


# Возвращает весь инвентарь страны в виде словаря
async def inventory_list(country: str) -> dict:
    connect = con(DATABASE_COUNTRIES_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT *
                    FROM countries_inventory
                    WHERE name = '{country}'
                    """)
    result = cursor.fetchone()
    connect.close()
    return dict(result) if result else {}

# Возвращает все фабрики страны в виде словаря
async def factory_list(country: str) -> dict:
    connect = con(DATABASE_COUNTRIES_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT *
                    FROM country_factories
                    WHERE name = '{country}'
                    """)
    result = cursor.fetchone()
    connect.close()
    return dict(result) if result else {}

# Показывает всю армию страны и ее баланс
async def give_army(interaction: Interaction) -> None:
    country = await give_country(interaction.user.mention)
    await interaction.response.defer(ephemeral=True)

    if not country:
        await interaction.followup.send('Балван! Ты не страна! Ну или это ошибке в базе...', ephemeral=True)
        return None
    
    inv = await inventory_list(country)
    embed_desc = ''

    for key, value in inv.items():
        
        if key not in ('name', 'Деньги') and int(value):
            embed_desc += key + ' - ' + str(int(value)) + '\n\n'
    
    embed = Embed(title=f'Баланс: {CURRENCY}{inv['Деньги']}', description=embed_desc)
    await interaction.followup.send(embed=embed, ephemeral=True)


# Показывает все фабрики страны и ее баланс
async def give_enterprise(interaction: Interaction) -> None:
    country = await give_country(interaction.user.mention)
    await interaction.response.defer(ephemeral=True)

    if not country:
        await interaction.followup.send('Балван! Ты не страна! Ну или это ошибке в базе...', ephemeral=True)
        return None
    
    inv = await factory_list(country)
    embed_desc = ''

    for key, value in inv.items():
        
        if key != 'name' and int(value):
            embed_desc += key + ' - ' + str(int(value)) + '\n\n'
    
    embed = Embed(title=f'Баланс: {CURRENCY}{await get_money(country)}', description=embed_desc)
    await interaction.followup.send(embed=embed, ephemeral=True)