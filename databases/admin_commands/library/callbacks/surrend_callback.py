from ..modules import Interaction, con, deps

# temp file
async def surrend_callback(interaction: Interaction, value: str):
    country = deps.Country(value)
    await country.change_surrend()

    await interaction.response.send_message('Страна подписана как сдавшиеся!', ephemeral=True)