from ..modules import give_country, Interaction, get_money, get_cost, get_country_info
from ..modals.buyModal import Buy

class BuyCallback:
    async def buy_callback(self, interaction: Interaction) -> None:
        # Проверяем является ли пользлватель страной
        item = ''.join(interaction.data['values']) 
        country = await give_country(interaction.user.mention)

        if not country:
            await interaction.response.edit_message(content= 'Вы не зарегистрированы!', view= None)
            return None
        
        ships = ['Верфь для подлодок', 'Верфь для эсминцев', 'Верфь для крейсеров', 'Верфь для линкоров']
        country_info = await get_country_info(country)

        if (item in ships) and not country_info['sea']:
            await interaction.response.edit_message(content= 'А может ты в начале выход к морю получишь?', view= None)
            return None

        
        # Если да спрашиваем сколько он хочет купить 
        modal = Buy(await get_money(country), await get_cost(item), country, item)
        await interaction.response.send_modal(modal)