from ..modules import Interaction, con, deps

# Temp file
async def no_surrend_callback(interaction: Interaction, value: str):
    country = deps.Country(value)
    await country.change_surrend()

    await interaction.response.send_message('Страна подписана как не сдавшиеся!', ephemeral=True)