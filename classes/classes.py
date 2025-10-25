from .library import con, Row, DATABASE_PATH, getinv, getfact, ROLE_PICKER_PATH



class Country:
    def __init__(self, name: str):
        self.name = name
        self.market_inventory = Market(name)
        self.items_inventory = getinv(name) 
        self.factories_inventory = getfact(name)

        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT is_busy
                        FROM roles
                        WHERE name = '{name}'
                        """)
        self.busy = (cursor.fetchone())[0]
        connect.close()

class Item:
    def __init__(self, name: str, quantity: int | None = None, price: int = 0, country: str | Country | None = None):
        self.name = name
        self.quantity = quantity if quantity != None else getinv(country, name)
        self.price = price
        
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
        self.market_inventory = {}
        self.name = country
        
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
                    quantity, price = value.split()
                    # if int(quantity):
                    self.market_inventory[name] = Item(name, int(quantity), int(price))
    
    def get_inv(self, quest: bool = False) -> dict:
        res = {}
        for name, item in self.market_inventory.items():
            if item.quantity or quest:
                res[name] = item
        return res
    
    def add_item(self, item: Item) -> None:
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        INSERT INTO market (name, {item.name})
                        VALUES ({self.name}, '{item.quantity} {item.price}')
        """)
        connect.commit()
        connect.close()
        self.market_inventory[item.name] = item
        return None
    
    def edit_item(self, item: Item) -> None:
        if not self.market_inventory:
            self.add_item(item)
            return None
        
        self.market_inventory[item.name] = item
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
        self.quantity = quantity if quantity != None else getfact(country, factory_name).quantity
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
        