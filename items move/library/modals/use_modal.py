from ..modules import Modal, TextInput, Interaction
from ..functions import remove_item

class UseModal(Modal):
    def __init__(self, item, country):
        super().__init__(title='Сколько всего было уничтожено или потрачено?')
        self.item = item
        self.country = country

        self.quantity = TextInput(label=f'Сюда пишите!', placeholder='Сейчас мы их поломаем >:)', required=True)
        self.add_item(self.quantity)
    
    async def on_submit(self, interaction: Interaction) -> None:
        quantity = int(self.quantity.value)
        count = 0

        try:
            count = int(await remove_item(self.item, quantity, self.country))
        except ValueError:
            await interaction.response.send_message('Думаешь ввел отрицательное число и самый умный?', ephemeral=True)
            return None
        await interaction.response.send_message(f'Все, нету больше твоих солдатиков, самолетиков или что там было. Теперь их у тебя `{count}`')