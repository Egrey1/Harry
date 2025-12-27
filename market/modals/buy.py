from ..library import Modal, TextInput, Interaction, con, deps

class Buy(Modal):
    def __init__(self, country: str, item: str, seller: str, positions: dict[str, dict]):
        super().__init__(title='Покупка позиции с рынка')
        self.country = country
        self.item = item
        self.positions = positions

        self.seller_info = None
        for countries in positions[item]['sellers']:
            if countries['country'] == seller:
                self.seller_info = countries
                break

        self.qty = TextInput(label=f'Вы покупаете у {seller}', placeholder=f"Всего {self.seller_info['qty']} по {deps.CURRENCY}{self.seller_info['price']} за штуку", required=True)
        self.add_item(self.qty)

    async def on_submit(self, interaction: Interaction):
        raw = (self.qty.value or '').strip()
        try:
            requested = int(raw)
        except ValueError:
            await interaction.response.send_message('Пожалуйста, введите корректное целое число количества.', ephemeral=True)
            return

        if requested <= 0:
            await interaction.response.send_message('Количество должно быть положительным.', ephemeral=True)
            return

        seller_qty = int(self.seller_info['qty'])
        buy_count = min(requested, seller_qty)

        if buy_count == 0:
            await interaction.response.send_message('У продавца нет доступного количества.', ephemeral=True)
            return

        price_per = int(self.seller_info['price'])
        total_price = buy_count * price_per

        buyer_country = self.country if isinstance(self.country, deps.Country) else deps.Country(self.country)
        seller_country = deps.Country(self.seller_info['country'])
        if not buyer_country or not seller_country:
            await interaction.response.send_message('Покупатель или продавец не найдены.', ephemeral=True)
            return

        buyer_money = int(buyer_country.balance)

        if buyer_money < total_price:
            buy_count = buyer_money // price_per
            total_price = buy_count * price_per

        if buy_count == 0:
            await interaction.response.send_message('У вас недостаточно денег для покупки.', ephemeral=True)
            return

        # Update seller market item
        market_item = seller_country.market.inventory.get(self.item)
        new_seller_qty = max(0, market_item.quantity - buy_count) if market_item else 0
        if market_item:
            if new_seller_qty == 0:
                seller_country.market.remove_item(self.item)
            else:
                market_item.quantity = new_seller_qty
                seller_country.market.edit_item(market_item)

        # Give items to buyer
        buyer_item = buyer_country.inventory.get(self.item)
        if buyer_item:
            buyer_item.edit_quantity(buyer_item.quantity + buy_count, buyer_country)
            buyer_item.quantity += buy_count
        else:
            from classes.game_objects import Item as GameItem
            new_item = GameItem(self.item, quantity=buy_count, price=0, country=buyer_country)
            new_item.edit_quantity(buy_count, buyer_country)
            buyer_country.inventory[self.item] = new_item

        # Transfer money via DB updates
        connect = con(deps.DATABASE_COUNTRIES)
        cursor = connect.cursor()
        cursor.execute('''
                       UPDATE countries_inventory
                       SET "Деньги" = "Деньги" - ?
                       WHERE name = ?
                       ''', (total_price, buyer_country.name))
        cursor.execute('''
                       UPDATE countries_inventory
                       SET "Деньги" = "Деньги" + ?
                       WHERE name = ?
                       ''', (total_price, seller_country.name))
        connect.commit()
        connect.close()

        await interaction.response.send_message(f'Успешно куплено `{buy_count} {self.item}` у {self.seller_info["country"]} за {deps.CURRENCY}{total_price}!', ephemeral=True)

