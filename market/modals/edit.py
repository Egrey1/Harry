from ..library import Modal, TextInput, Interaction, con, deps

class Edit(Modal):
    def __init__(self, country: str | deps.Country, item: str | deps.Item, have: str, on_market: str):
        super().__init__(title='Тут можешь отредактировать свою позицию!')
        self.item_name = item if isinstance(item, str) else item.name
        self.on_market = on_market.split()
        self.country = country if isinstance(country, deps.Country) else deps.Country(country)
        self.have = have


        self.count = TextInput(label='Сколько прибавить/убавить?', placeholder=f'На рынке - {self.on_market[0]}. В инвентаре - {have}', required=False)
        self.price = TextInput(label='Введите новую цену', placeholder=f'Сейчас - {self.on_market[1]}', required=False)
        self.add_item(self.count)
        self.add_item(self.price)
    
    async def on_submit(self, interaction: Interaction):
        delta_count = int(self.count.value) if self.count.value else 0
        new_price = int(self.price.value) if self.price.value else int(self.on_market[1])

        current_count = int(self.on_market[0])
        updated_count = 0

        if delta_count > self.have:
            delta_count = self.have
        updated_count = current_count + delta_count

        if updated_count < 0:
            delta_count = -current_count
            updated_count = 0

            

        if new_price <= 0:
            await interaction.response.send_message(f'Цена должна быть положительным числом!', ephemeral=True)
            return


        connect = con(deps.DATABASE_COUNTRIES_PATH)
        cursor = connect.cursor()

        col = self.item_name
        new_value = f"{updated_count} {new_price}"

        cursor.execute(f"""
                       UPDATE market 
                       SET `{col}` = ? 
                       WHERE country_id = ?
                       """, (new_value, self.country.id))
        
        cursor.execute(f"""
                       UPDATE countries_inventory
                       SET `{col}` = `{col}` - ?
                       WHERE country_id = ?
                       """, (delta_count, self.country.id))

        connect.commit()
        connect.close()

        if updated_count == 0:
            await interaction.response.send_message(f'Твои `{self.item_name}` удалены >:)', ephemeral=True)
            return
        
        if not self.count.value and not self.price.value:
            await interaction.response.send_message(f'Ты вызвал команду чтоб на кнопки потыкать?', ephemeral=True)
            return
        
        await interaction.response.send_message(f'Готово! `{self.item_name}` - `{updated_count}` по `{deps.CURRENCY}{new_price}` за единицу!', ephemeral=True)