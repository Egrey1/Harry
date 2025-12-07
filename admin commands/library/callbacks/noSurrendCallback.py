from ..modules import Interaction, con, deps

# Temp file
async def no_surrend_callback(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)

    country = ''.join(interaction.data['values'])
    connect = con(ROLE_PICKER_PATH)
    cursor = connect.cursor()

    cursor.execute(f"""
                    UPDATE roles
                    SET surrender = NULL
                    WHERE name = '{country}'
                    """)
    connect.commit()
    connect.close()

    await interaction.followup.send('Страна подписана как не сдавшиеся!', ephemeral=True)