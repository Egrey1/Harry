from ..modules import (Interaction, 
                        #give_country, get_money, get_cost, get_country_info | USE OBJECTS! Country, Factory 
                       deps)
#from ..modals.buyModal import Buy
from ..modals import Buy

class BuyCallback:
    async def buy_callback(self, interaction: Interaction) -> None:
        # Проверяем является ли пользлватель страной
        #item = ''.join(interaction.data['values'])
        item = deps.Item(interaction.data['values'][0])        
        country = await give_country(interaction.user.mention)

        if not country:
            await interaction.response.edit_message(content= 'Вы не зарегистрированы!', embed= None)
            return None
        
        ships = ['Верфь для подлодок', 'Верфь для эсминцев', 'Верфь для крейсеров', 'Верфь для линкоров'] # DELETE THIS LINE
        country_info = await get_country_info(country)

        #if (item in ships) and not country_info['sea']:
        if item.is_ship and not item.sea:
            await interaction.response.edit_message(content= 'А может ты в начале выход к морю получишь?', embed= None)
            return None

        
        # Если да спрашиваем сколько он хочет купить 
        modal = Buy(await get_money(country), await get_cost(item), country, item)
        await interaction.response.send_modal(modal)