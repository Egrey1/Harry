from ..library.modules import hybrid_command, SelectOption, Select, View
from ..library.functions import give_all_countries

class ChangeNicknameCommand:
    @hybrid_command(name= 'change_nickname')
    async def change_nickname(self, ctx):

        countries = await give_all_countries()
        view = View()
        options = []

        for country in countries:
            options.append(SelectOption(label= country, value= country))

        select = Select(placeholder= 'What country are you changing the nickname for?', options= options)
        view.add_item(select)

        select.callback = change_nickname_callback


    
