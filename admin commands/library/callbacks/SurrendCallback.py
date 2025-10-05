from ..modules import Interaction, con, ROLE_PICKER_PATH, give_country
from ..functions import unreg_function

async def surrend_callback(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)

    country = ''.join(interaction.data['values'])
    connect = con(ROLE_PICKER_PATH)
    cursor = connect.cursor()

    cursor.execute(f"""
                    UPDATE roles
                    SET surrender = ' '
                    WHERE name = '{country}'
                    """)
    
    await unreg_function(await give_country(interaction.user.mention), interaction)
    
    connect.commit()
    connect.close()

    await interaction.followup.send('Страна подписана как сдавшиеся!', ephemeral=True)