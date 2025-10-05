from ..modules import give_country, Interaction, get_money, get_cost
from ..modals.buyModal import Buy

class BuyCallback:
    async def buy_callback(self, interaction: Interaction) -> None:
        # Проверяем является ли пользлватель страной
        item = ''.join(interaction.data['values']) 
        country = await give_country(interaction.user.mention)

        if not country:
            await interaction.response.edit_message(content= 'Вы не зарегистрированы!', view= None)
            return None
        
        # Если да спрашиваем сколько он хочет купить 
        modal = Buy(await get_money(country), await get_cost(item), country, item)
        await interaction.response.send_modal(modal)