from discord import Intents
from sqlite3 import connect as con

#Проверяет есть ли пользователь в списке стран. Возвращает пустую строку если нет
async def give_country(mention: str) -> str:
    connect = con(DATABASE_ROLE_PICKER)
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT name
                    FROM roles
                    WHERE is_busy = '{mention}'
                    """)
    result = cursor.fetchone()
    connect.close()
    try:
        return result[0]
    except:
        return ''

# Возвращает текущие деньги страны
async def get_money(country: str) -> int:
    connect = con(DATABASE_COUNTRIES)
    cursor = connect.cursor()
    cursor.execute(f"""
                   SELECT "Деньги"
                   FROM countries_inventory
                   WHERE name = '{country}'
                   """)
    res = cursor.fetchone()[0]
    connect.close()

    return int(res)

# Возвращает стоимость товара
async def get_cost(item: str) -> int:
    connect = con(DATABASE_COUNTRIES)
    cursor = connect.cursor()
    cursor.execute(f"""
                   SELECT "cost"
                   FROM factories
                   WHERE name = '{item}'
                   """)
    res = cursor.fetchone()[0]
    connect.close()

    return int(res)

# Возвращает инвентарь страны в виде словаря
async def get_inventory(country: str) -> dict:
    from sqlite3 import Row

    connect = con(DATABASE_COUNTRIES)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT *
                    FROM countries_inventory
                    WHERE name = '{country}'
                   """)
    res = cursor.fetchone()
    connect.close()

    return dict(res) if res else {}


DATABASE_ROLE_PICKER = 'databases/role-picker.db'
DATABASE_COUNTRIES = 'databases/countries.db'

CURRENCY = '£'

TOKEN = open('TOKEN.txt').readline()
intents = Intents.all()
PREFIX = 'detri!'
