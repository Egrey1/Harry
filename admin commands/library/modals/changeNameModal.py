from ..modules import Modal, TextInput, Interaction, con, DATABASE_PATH

class ChangeNickNameModal(Modal):
    def __init__(self, country: str):
        super().__init__(title="Выбор количества")  
        self.country = country
        
        self.new_nickname= TextInput(label= 'What is new nickname?', placeholder= 'Write here', required= True)
        self.add_item(self.new_nickname)

    async def on_submit(self, interaction: Interaction) -> None:
        new_nickname = self.new_nickname

        connect = con(DATABASE_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                       UPDATE roles
                       SET nickname = '{new_nickname}'
                       WHERE name = '{self.country}'
                       """)
        connect.commit()
        connect.close()

        # 

        interaction.response.send_message(content= 'Successfully changed nickname', ephemeral= True)