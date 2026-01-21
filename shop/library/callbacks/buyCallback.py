from ..modules import (Interaction, 
                        #give_country, get_money, get_cost, get_country_info | USE OBJECTS! Country, Factory 
                       deps)
#from ..modals.buyModal import Buy
from ..modals import Buy

class BuyCallback:
    async def buy_callback(self, interaction: Interaction) -> None:
        # Проверяем является ли пользлватель страной
        #item = ''.join(interaction.data['values'])
        factory = deps.Factory(interaction.data['values'][0])        
        country = deps.Country(interaction.user.mention)

        if not country.busy:
            await interaction.response.edit_message(content= 'Вы не зарегистрированы!', embed= None)
            return None

        #if (item in ships) and not country_info['sea']:
        if deps.Item(factory.produces).is_ship and not country.sea:
            await interaction.response.edit_message(content= 'А может ты в начале выход к морю получишь?', embed= None)
            return None

        deps.Factory
        # Если да спрашиваем сколько он хочет купить 
        modal = Buy(country.balance, factory.cost, country, factory)
        await interaction.response.send_modal(modal)