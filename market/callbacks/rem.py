from ..library import Interaction, con, DATABASE_COUNTRIES

async def rem(interaction: Interaction, country: str):
    item = interaction.data['values'][0]

    connect = con(DATABASE_COUNTRIES)
    cursor = connect.cursor()
    cursor.execute(f"""
                    UPDATE market
                    SET `{item}` = 0
                    WHERE `name` = ?
                    """, (country,))
    connect.commit()
    connect.close()
    await interaction.response.send_message(f'Позиция `{item}` успешно удалена с рынка!', ephemeral=True)