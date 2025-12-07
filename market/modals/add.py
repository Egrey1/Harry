from ..library import Modal, TextInput, Interaction, con, deps
from ..library.functions import give_items

class Add(Modal):
    def __init__(self, country, item, item_count: int):
        super().__init__(title='Добавление позиции на рынок')
        self.country = country
        self.item = item
        self.item_count = item_count

        # Inputs
        self.count = TextInput(label='Количество', placeholder=f'У вас есть: {self.item_count}', required=True)
        self.price = TextInput(label='Цена за единицу', placeholder='Введите цену за единицу', required=True)
        self.add_item(self.count)
        self.add_item(self.price)

    async def on_submit(self, interaction: Interaction):
        count = int(self.count.value)
        price = int(self.price.value)
        if count > self.item_count:
            await interaction.response.send_message(f'А вот нет у тебя столько!', ephemeral=True)
            return
        elif count <= 0 or price <= 0:
            await interaction.response.send_message(f'Опять хитрец нашелся, нельзя отрицательные числа вводить!', ephemeral=True)
            return

        connect = con(DATABASE_COUNTRIES)
        cursor = connect.cursor()


# ----------------------------------GPT CODE------------------------------------------
        col = self.item

        # Get existing value for this country/item
        cursor.execute(f"""
                       SELECT `{col}` 
                       FROM market 
                       WHERE name = ?
                       """, (self.country,))
        row = cursor.fetchone()

        new_value = f"{count} {price}"

        if row is None:
            # No row for this country yet -> insert a new row with this item
            cursor.execute(f"""
                           INSERT INTO market (name, `{col}`) 
                           VALUES (?, ?)
                           """, (self.country, new_value))
        else:
            existing = row[0]
            if not existing:
                # Column empty -> just set it
                cursor.execute(f"""
                               UPDATE market SET `{col}` = ? 
                               WHERE name = ?
                               """, (new_value, self.country))
            else:
                # Merge quantities: parse existing as "qty price"
                try:
                    existing_qty_str, existing_price_str = str(existing).split()
                    existing_qty = int(existing_qty_str)
                except Exception:
                    # If parsing fails, fallback to overwrite behavior to avoid crashing
                    existing_qty = 0

                # Sum quantities and set price to the new provided price (adjust if you want different behavior)
                merged_qty = existing_qty + count
                merged_value = f"{merged_qty} {price}"
                cursor.execute(f"""
                               UPDATE market 
                               SET `{col}` = ? 
                               WHERE name = ?
                               """, (merged_value, self.country))

        # Now subtract the items from the country's inventory atomically.
        # If the inventory doesn't contain enough items, rollback and inform the user.
        if count > 0:
            cursor.execute(
                f"UPDATE countries_inventory SET `{col}` = `{col}` - ? WHERE name = ? AND `{col}` >= ?",
                (count, self.country, count),
            )
            if cursor.rowcount == 0:
                connect.rollback()
                connect.close()
                await interaction.response.send_message('В инвентаре недостаточно предметов чтобы добавить столько на рынок', ephemeral=True)
                return

        connect.commit()
        connect.close()
        # ----------------------------------GPT CODE END------------------------------------------

        await interaction.response.send_message(f'Успешно добавлено `{count} {self.item}` по цене `{price}` за единицу на рынок!', ephemeral=True)