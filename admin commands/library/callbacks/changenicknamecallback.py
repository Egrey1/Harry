from ..modules import Interaction, deps
from ..modals.changeNameModal import ChangeNickNameModal

class ChangeNickname:
    async def change_nickname_callback(self, interaction: Interaction):
        country_changed = deps.Country(interaction.data['values'])
        modal = ChangeNickNameModal(country_changed)
        await interaction.response.send_modal(modal)
        

        
        

        
        