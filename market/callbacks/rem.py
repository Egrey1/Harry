from ..library import Interaction, deps, con

async def rem(interaction: Interaction, country: deps.Country):
    item_name = interaction.data['values'][0]
    country = str(country)

    connect = con(deps.DATABASE_COUNTRIES_PATH)
    cursor = connect.cursor()

    cursor.execute(f"""
                   SELECT `{item_name}`
                   FROM market
                   WHERE name = '{country}'
                   """)
    have = (cursor.fetchone()[0]).split()[0]

    cursor.execute(f"""
                    UPDATE market
                    SET `{item_name}` = 0
                    WHERE name = ?
                    """, (country,))
    
    cursor.execute(f"""
                   UPDATE countries_inventory
                   SET `{item_name}` = `{item_name}` + {have}
                   WHERE name = '{country}'
                   """)
    connect.commit()
    connect.close()
    await interaction.response.send_message(f'Позиция `{item_name}` успешно удалена с рынка!', ephemeral=True)