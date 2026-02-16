from ..library import Interaction, deps, con

async def rem(interaction: Interaction, country: deps.Country):
    item_name = interaction.data['values'][0]
    country = country

    connect = con(deps.DATABASE_COUNTRIES_PATH)
    cursor = connect.cursor()

    cursor.execute(f"""
                   SELECT `{item_name}`
                   FROM market
                   WHERE country_id = '{country.id}'
                   """)
    have = (cursor.fetchone()[0]).split()[0]

    cursor.execute(f"""
                    UPDATE market
                    SET `{item_name}` = 0
                    WHERE country_id = ?
                    """, (country.id,))
    
    cursor.execute(f"""
                   UPDATE countries_inventory
                   SET `{item_name}` = `{item_name}` + {have}
                   WHERE country_id = '{country.id}'
                   """)
    connect.commit()
    connect.close()
    await interaction.response.send_message(f'Позиция `{item_name}` успешно удалена с рынка!', ephemeral=True)