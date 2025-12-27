from ..modules import Modal, TextInput, Interaction
from ..functions import transfer_item


class Quantity(Modal):
    def __init__(self, item_name: str, had: int, country_from, country_to):
        super().__init__(title='Введите количество')
        self.item_name = item_name
        self.had = int(had)
        self.country_from = country_from
        self.country_to = country_to

        self.quantity = TextInput(label=f'У вас {self.had}', placeholder='Введите количество для передачи', required=True)
        self.add_item(self.quantity)
    
    
    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            q = int(self.quantity.value)
        except ValueError:
            await interaction.followup.send('Введите целое число!', ephemeral=True)
            return

        if q <= 0:
            await interaction.followup.send('Введите положительное число!', ephemeral=True)
            return

        if q > self.had:
            await interaction.followup.send('У вас нет столько!', ephemeral=True)
            return

        left, new_to = await transfer_item(self.item_name, q, self.country_from, self.country_to)
        await interaction.followup.send(f'Передано: `{q}`. У вас осталось: `{left}`', ephemeral=True)