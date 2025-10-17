from ..library import Modal, TextInput, CURRENCY, Interaction, con, DATABASE_COUNTRIES
from ..library.functions import country_money

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


        self.qty = TextInput(label=f'Вы покупаете у {seller}', placeholder=f'Всего {self.seller_info['qty']} по {CURRENCY}{self.seller_info['price']} за штуку', required=True)
        self.add_item(self.qty)

    async def on_submit(self, interaction: Interaction):
        buy_count = min(int(self.qty.value), self.seller_info['qty'])

        if buy_count < 0:
            await interaction.response.send_message(f'Опять эти гении', ephemeral=True)
            return
        if buy_count == 0:
            await interaction.response.send_message(f'С каждым разом я все больше и больше поражаюсь вами...', ephemeral=True)
            return


        total_price = buy_count * self.seller_info['price']
        buyer_money = await country_money(self.country)

        if buyer_money < total_price:
            buy_count = buyer_money // self.seller_info['price']
            total_price = buy_count * self.seller_info['price']


        connect = con(DATABASE_COUNTRIES)
        cursor = connect.cursor()

        # update market list
        cursor.execute(f"""
                       UPDATE market 
                       SET `{self.item}` = ?
                       WHERE name = ?
                       """, (f"{self.seller_info['qty'] - buy_count} {self.seller_info['price']}", self.seller_info['country']))
        
        # give items to buyer
        cursor.execute(f"""
                       UPDATE countries_inventory
                       SET `{self.item}` = `{self.item}` + ?
                       WHERE name = ?
                       """, (buy_count, self.country))
        
        # take money from buyer
        cursor.execute(f"""
                        UPDATE countries_inventory
                        SET Деньги = Деньги - ?
                        WHERE name = ?
                        """, (total_price, self.country))
        
        # give money to seller
        cursor.execute(f"""
                        UPDATE countries_inventory
                        SET Деньги = Деньги + ?
                        WHERE name = ?
                        """, (total_price, self.seller_info['country']))
        
        connect.commit()
        connect.close()

        await interaction.response.send_message(f'Успешно куплено `{buy_count} {self.item}` у {self.seller_info["country"]} за {CURRENCY}{total_price}!', ephemeral=True)

