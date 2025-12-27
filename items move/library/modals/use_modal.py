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
        raw = (self.quantity.value or '').strip()
        try:
            quantity = int(raw)
        except ValueError:
            await interaction.response.send_message('Пожалуйста, введите целое число больше нуля.', ephemeral=True)
            return None

        if quantity <= 0:
            await interaction.response.send_message('Количество должно быть положительным.', ephemeral=True)
            return None

        original_item = self.country.inventory.get(self.item)
        original_qty = original_item.quantity if original_item else 0

        try:
            new_qty = await remove_item(self.item, quantity, self.country)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return None

        removed = original_qty - int(new_qty)
        await interaction.response.send_message(f'Удалено `{removed}` предмет(ов). Осталось `{new_qty}`.', ephemeral=True)