from .library import (con, Row, DATABASE_PATH, 
                      getinv, getfact, getbalance, 
                      ROLE_PICKER_PATH, Interaction, bot, 
                      GUILD, roles_id, Context)



class Country:
    def __init__(self, name: str):
        self.name = name
        self.market = Market(name)
        self.inventory = getinv(name) 
        self.factories = getfact(name)
        self.balance = getbalance(name)


        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        
        cursor.execute(f"""
                        SELECT is_busy, surrend, sea, assembly, nickname
                        FROM roles
                        WHERE name = '{name}'
                        """)
        fetch = cursor.fetchone()
        
        self.busy = fetch[0]
        self.surrend = fetch[1]
        self.sea = fetch[2]
        self.assembly = fetch[3]
        self.nickname = fetch[4]
        
        connect.close()
    


    async def change_surrend(self, interaction: Interaction | None = None):
        name = interaction.data['values'][0] if interaction else self.name
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        
        if self.surrend:
            cursor.execute(f"""
                            UPDATE roles
                            SET surrend = NULL
                            WHERE name = {name}
            """)
            # self.unreg(interaction)
            self.surrend = None
            
        else:
            cursor.execute(f"""
                            UPDATE roles
                            SET surrend = ' '
                            WHERE name = {self.name}
            """)
            self.surrend = ' '
            
        connect.commit()
        connect.close()
        


    async def change_nickname(self, new_nickname: str):
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        
        user_mention = self.busy

        cursor.execute(f"""
                       UPDATE roles
                       SET nickname = '{new_nickname}'
                       WHERE name = '{self.name}'
                       """)
        connect.commit()
        connect.close()
        
        if user_mention:
            try:
                member = bot.get_guild(GUILD).get_member(int(user_mention[2:-1]))
                await member.edit(nick= new_nickname)
            except:
                pass



    async def unreg(self, interaction: Interaction | Context | None = None):
        if not self.busy:
            return None
        
        user = interaction.user # if interaction else bot.get_guild(GUILD)
        for id in roles_id.values():
            try:
                role = interaction.guild.get_role(id) 
                await user.remove_roles(role) 
            except:
                continue

        try:
            unreg = interaction.guild.get_role(1344519330091503628)
            await user.add_roles(unreg)  
        except:
            pass

        try:
            await user.edit(nick='') 
        except:
            pass
        
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                        UPDATE roles
                        SET is_busy = null
                        WHERE is_busy = '{self.busy}'
                        """)
        connect.commit()
        connect.close()
        self.busy = None
                

class Item:
    def __init__(self, name: str, quantity: int | None = None, price: int = 0, country: str | Country | None = None):
        self.name = name
        self.quantity = quantity if quantity != None else (getinv(country, name).quantity if country else 0)
        self.price = price
        self.purchasable = name not in ['Пехота', 'Морпехота', 'Десантник', 'Кавалерия', 'Деньги']
        self.is_ship = name in ['Подлодка', 'Эсминец', 'Крейсер', 'Линкор']
        
    def edit_quantity(self, quantity: int, country: str | Country) -> None:
        country = country.name if type(country) == Country else country
        self.quantity = quantity
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        UPDATE country_inventories
                        SET `{self.name}` = {quantity}
                        WHERE `name` = '{country}'
        """)
        return None

class Market:
    def __init__(self, country: str | Country):
        country = country.name if type(country) == Country else country
        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        self.inventory = {}
        self.name = country.name if type(country) == Country else country
        
        try:
            cursor.execute(f"""
                SELECT *
                FROM market
                WHERE name = '{country}'
            """)
        except:
            cursor.execute(f"""
                INSERT INTO market (name)
                VALUES ('{country}')
            """)
            connect.commit()
            
            cursor.execute(f"""
                SELECT *
                FROM market
                WHERE name = '{country}'
            """)
        res = dict(cursor.fetchone())
        connect.close()
        if res:
            for name, value in res:
                if name != 'name':
                    quantity, price = value.split() if len(value.split()) == 2 else ['0', '0']
                    # if int(quantity):
                    self.inventory[name] = Item(name, int(quantity), int(price))
    
    def get_inv(self, quest: bool = False) -> dict:
        res = {}
        for name, item in self.inventory.items():
            if item.quantity or quest:
                res[name] = item
        return res
    
    def add_item(self, item: Item) -> None:
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        INSERT INTO market (name, {item.name})
                        VALUES ('{self.name}', '{item.quantity} {item.price}')
        """)
        connect.commit()
        connect.close()
        self.inventory[item.name] = item
        return None
    
    def edit_item(self, item: Item) -> None:
        if not self.inventory:
            self.add_item(item)
            return None
        
        self.inventory[item.name] = item
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        UPDATE market
                        SET `{item.name}` = '{str(item.quantity)} {str(item.price)}'
                        WHERE name = {self.name}
        """)
        connect.commit()
        connect.close()
        return None
    
    def remove_item(self, item: Item | str) -> None:
        item = item.name if type(item) == Item else item
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        UPDATE market
                        SET `{item}` = '0 0'
                        WHERE name = '{self.name}'
        """)
        connect.commit()
        connect.close()
        return None

class Factory:
    def __init__(self, factory_name: str, quantity: int | None = None, country: str | Country | None = None):
        self.name = factory_name
        self.quantity = quantity if quantity != None else (getfact(country, factory_name).quantity if country else 0)
        self.country = Country(country)
        
        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT *
                        FROM factories
                        WHERE name = {factory_name}
        """)
        fetch = cursor.fetchone()
        connect.close()
        
        self.produces = fetch['produces_key']
        self.count = float(fetch['count'])
        self.desc = fetch['desc']
        self.cost = int(fetch['cost'])
        
    def edit_quantity(self, quantity: int, country: str | Country) -> None:
        country = country.name if type(country) == Country else country
        self.quantity = quantity
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        UPDATE countries_factory
                        SET `{self.name}` = {quantity}
                        WHERE `name` = '{country}'
        """)
        return None