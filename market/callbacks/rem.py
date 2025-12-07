from ..library import Interaction, deps

async def rem(interaction: Interaction, country: str):
    item = interaction.data['values'][0]

    connect = con(DATABASE_COUNTRIES)
    cursor = connect.cursor()

    cursor.execute(f"""
                   SELECT `{item}`
                   FROM market
                   WHERE name = {country}
                   """)
    have = (cursor.fetchone()[0]).split()[0]

    cursor.execute(f"""
                    UPDATE market
                    SET `{item}` = 0
                    WHERE name = ?
                    """, (country,))
    
    cursor.execute(f"""
                   UPDATE countries_inventory
                   SET `{item}` = `{item}` + {have}
                   WHERE name = '{country}'
                   """)
    connect.commit()
    connect.close()
    await interaction.response.send_message(f'Позиция `{item}` успешно удалена с рынка!', ephemeral=True)