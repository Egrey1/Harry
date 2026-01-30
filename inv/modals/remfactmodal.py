from ..library import Modal, TextInput, deps, Interaction

class RemFactModal(Modal):
    def __init__(self, factory: deps.Factory):
        super().__init__(title='Разрушение фабрик')
        
        self.factory = factory

        self.quantity = TextInput(
            label=f'Сколько фабрик "{factory.name}" вы хотите разрушить? (У вас {factory.quantity})', 
            placeholder='Введите количество',
            required=True
        )
        self.add_item(self.quantity)

    async def on_submit(self, interaction: Interaction) -> None:
        try:
            quantity = int(self.quantity.value)
        except ValueError:
            await interaction.response.send_message('Введите корректное число!', ephemeral=True)
            return
            
        if quantity <= 0:
            await interaction.response.send_message('Количество должно быть положительным числом!', ephemeral=True)
            return
        if quantity > self.factory.quantity:
            quantity = self.factory.quantity  # Ограничиваем до максимума
        
        # Разрушаем фабрики - нужно получить страну из контекста
        country = deps.Country(self.factory.country.name if self.factory.country else interaction.user.mention)
        
        if not country.busy:
            await interaction.response.send_message('Ошибка: не удалось определить страну!', ephemeral=True)
            return
        
        self.factory.edit_quantity(self.factory.quantity - quantity, country)
        
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f'Вы успешно разрушили {quantity} фабрик "{self.factory.name}".', ephemeral=True)