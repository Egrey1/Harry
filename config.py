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
                   SELECT cost
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

# Возвращает всю информацию по ролям для страны
async def get_country_info(country: str) -> dict:
    from sqlite3 import Row

    connect = con(DATABASE_ROLE_PICKER)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT *
                    FROM roles
                    WHERE name = '{country}'
                   """)
    res = cursor.fetchone()
    connect.close()

    return dict(res) if res else {}

DATABASE_ROLE_PICKER = 'databases/role-picker.db'
DATABASE_COUNTRIES = 'databases/countries.db'

CURRENCY = '£'
RP_ROLES = {'COUNTRY': 1353608772458905671, 'surrender': 1361802354059378708, 'sea': 1357681946276266044, 'assambley': 1357679628243959862, 'LEAGUE': 1353894726847430766, 'gensec': 1358783484046348471, 'soviet': 1357679674410664076, 'PARAMS': 1358763645538009119}
CHANNEL_FOR_UPDATE_ID = 1344823587093352569
GUILD = 1344423355293372488
game_state = {'game_started': True}

TOKEN = open('TOKEN.txt').readline()
intents = Intents.all()
PREFIX = '!'
