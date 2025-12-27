from ..modules import Interaction, deps
from ..modals.changeNameModal import ChangeNickNameModal

class ChangeNickname:
    async def change_nickname_callback(self, interaction: Interaction, value: str):
        country_changed = deps.Country(value)
        modal = ChangeNickNameModal(country_changed)
        await interaction.response.send_modal(modal)
        

        
        

        
        