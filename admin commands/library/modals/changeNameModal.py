from ..modules import Modal, TextInput, Interaction, con, deps
from ..functions import is_busy

class ChangeNickNameModal(Modal):
    def __init__(self, country: Country):
        super().__init__(title="Поменять никнейм")  
        self.country = country
        
        self.new_nickname= TextInput(label= 'Новое значение', placeholder= 'Флаг | название', required= True)
        self.add_item(self.new_nickname)

    async def on_submit(self, interaction: Interaction) -> None:
        new_nickname = self.new_nickname.value
        self.country.change_nickname(new_nickname)
        await interaction.response.send_message(content= 'Successfully changed nickname', ephemeral= True)