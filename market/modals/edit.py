from ..library import Modal, TextInput, Interaction, con, deps

class Edit(Modal):
    def __init__(self, country: str | deps.Country, item: str, have: str, on_market: str):
        super().__init__(title='Тут можешь отредактировать свою позицию!')
        self.item = item
        self.on_market = on_market.split()
        self.country_name = country if isinstance(country, str) else country.name
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

        col = self.item
        new_value = f"{updated_count} {new_price}"

        cursor.execute(f"""
                       UPDATE market 
                       SET `{col}` = ? 
                       WHERE name = ?
                       """, (new_value, self.country_name))
        
        cursor.execute(f"""
                       UPDATE countries_inventory
                       SET `{col}` = `{col}` - ?
                       WHERE name = ?
                       """, (delta_count, self.country_name))

        connect.commit()
        connect.close()

        if updated_count == 0:
            await interaction.response.send_message(f'Твои `{self.item}` удалены >:)', ephemeral=True)
            return
        
        if not self.count.value and not self.price.value:
            await interaction.response.send_message(f'Ты вызвал команду чтоб на кнопки потыкать?', ephemeral=True)
            return
        
        await interaction.response.send_message(f'Готово! `{self.item}` - `{updated_count}` по `{deps.CURRENCY}{new_price}` за единицу!', ephemeral=True)