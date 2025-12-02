from discord import Intents, SelectOption, TextChannel
from discord.ext.commands import Context, Bot
import discord.utils as utils
from sqlite3 import connect as con
import dependencies as deps

#Проверяет есть ли пользователь в списке стран. 
async def give_country(mention: str) -> deps.Country | False:
    connect = con(deps.DATABASE_ROLE_PICKER)
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT name
                    FROM roles
                    WHERE is_busy = '{mention}'
                    """)
    result = cursor.fetchone()
    connect.close()
    return deps.Country(result[0]) if result[0] else False

async def all_countries_option(context: Context, countries, page: int) -> int:
    return [SelectOption(label= countries[i], value=countries[i]) for i in range((page - 1) * deps.PAGE_SIZE, min((page) * deps.PAGE_SIZE, len(countries))) if i < len(countries)]

# Возвращает текущие деньги страны
async def get_money(country: str) -> int:
    connect = con(deps.DATABASE_COUNTRIES)
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
    connect = con(deps.DATABASE_COUNTRIES)
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

    connect = con(deps.DATABASE_COUNTRIES)
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

    connect = con(deps.DATABASE_ROLE_PICKER)
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

def get_channel(name: str) -> TextChannel:
    connect = con(deps.DATABASE_CONFIG)
    cursor = connect.cursor()
    cursor.execute(f"""
                   SELECT {name}
                   FROM channels
                   """)
    id = int(cursor.fetchone()[0])
    connect.close()
    role = deps.guild.get_role(id)
    if role:
        return role
    
    names = {
        'event': '📣┃события',
        'war': '📰┃новости-стран',
        'news': '🔥┃войны'
    }
    return utils.get(deps.guild.channels, names[name])

def config():
    """Присваивает всем переменным из dependencies.py их значения"""
    deps.CHANNEL_FOR_UPDATE_ID = 1344823587093352569 
    deps.guild_id = 1344423355293372488
    deps.guild = deps.bot.get_guild(deps.guild_id)
    deps.game_state = {'game_started': True}
    deps.PAGE_SIZE = 25
    deps.TOKEN = open('TOKEN.txt').readline()
    deps.intents = Intents.all()
    deps.PREFIX = '!'
    deps.CURRENCY = '£'
    deps.DATABASE_ROLE_PICKER = 'databases/role-picker.db'
    deps.DATABASE_COUNTRIES = 'databases/countries.db'
    deps.DATABASE_FOCUS = 'databases/focuses.db'
    deps.DATABASE_CONFIG = 'databases/config.db'
    deps.bot = Bot(command_prefix=deps.PREFIX, intents=deps.intents)
    deps.RP_ROLES = {'COUNTRY': 1353608772458905671, 'surrender': 1361802354059378708, 
            'sea': 1357681946276266044, 'assambley': 1357679628243959862, 
            'LEAGUE': 1353894726847430766, 'gensec': 1358783484046348471, 
            'soviet': 1357679674410664076, 'PARAMS': 1358763645538009119}


# from classes import *