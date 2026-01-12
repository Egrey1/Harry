from .modules import (con, 
                      Row, Interaction, Embed,
                      deps)


# Возвращает весь инвентарь страны в виде словаря
async def inventory_list(country: str) -> dict:
    connect = con(deps.DATABASE_COUNTRIES_PATH)
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
    connect = con(deps.DATABASE_COUNTRIES_PATH)
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
    country = deps.Country(interaction.user.mention)

    if not country.busy:
        await interaction.response.send_message('Балван! Ты не страна! Ну или это ошибка в базе...', ephemeral=True)
        return None

    items = []
    for name, item in country.inventory.items():
        if name in ('name', 'Деньги'):
            continue
        qty = getattr(item, 'quantity', 0)
        if qty:
            items.append(f"{name} - {qty}")

    embed_desc = '\n\n'.join(items) if items else 'Пусто'
    balance = getattr(country, 'balance', 0)
    embed = Embed(title=f"Баланс: {deps.CURRENCY}{balance}", description=embed_desc)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Показывает все фабрики страны и ее баланс
async def give_enterprise(interaction: Interaction) -> None:
    country = deps.Country(interaction.user.mention)

    if not country.busy:
        await interaction.response.send_message('Балван! Ты не страна!', ephemeral=True)
        return None

    factories = country.factories
    items = []

    for name, factory in factories.items():
        factory: deps.Factory
        qty = factory.quantity if factory else None
        if qty is None:
            qty = 0
        if name != 'name' and int(qty):
            items.append(f"{name} - {qty}")

    embed_desc = '\n\n'.join(items) if items else 'Пусто'
    balance = getattr(country, 'balance', 0)
    embed = Embed(title=f"Баланс: {deps.CURRENCY}{balance}", description=embed_desc)
    await interaction.response.send_message(embed=embed, ephemeral=True)