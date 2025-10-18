from ..modules import Modal, TextInput, Interaction, con, ROLE_PICKER_PATH
from ..functions import is_busy

class ChangeNickNameModal(Modal):
    def __init__(self, country: str):
        super().__init__(title="Change Nickname Prompt")  
        self.country = country
        
        self.new_nickname= TextInput(label= 'What do you want to change the nickname to?', placeholder= 'Write here', required= True)
        self.add_item(self.new_nickname)

    async def on_submit(self, interaction: Interaction) -> None:
        new_nickname = self.new_nickname.value

        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        
        user_mention = await is_busy(self.country)

        cursor.execute(f"""
                       UPDATE roles
                       SET nickname = '{new_nickname}'
                       WHERE name = '{self.country}'
                       """)
        connect.commit()
        connect.close()

        
        
        # user_mention = <@12312312>
        if user_mention:
            try:
                member = interaction.guild.get_member(int(user_mention[2:-1]))
                await member.edit(nick= new_nickname)
            except:
                pass
            


        await interaction.response.send_message(content= 'Successfully changed nickname', ephemeral= True)