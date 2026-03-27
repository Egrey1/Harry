from discord import Intents, SelectOption, TextChannel
from discord.ext.commands import Context, Bot
import discord.utils as utils
from sqlite3 import connect as conyto
import dependencies as deps
import logging
from dotenv import load_dotenv
from os import getenv
import classes as cl

def get_channel(name: str) -> TextChannel:
    from sqlite3 import connect as con
    connect = con(deps.DATABASE_CONFIG_PATH)
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
        'events': '📣┃события',
        'wars': '📰┃новости-стран',
        'news': '🔥┃войны'
    }
    return utils.get(deps.guild.channels, names[name])

def first_config():
    """Создает экземпляр бота для последующего запуска"""
    load_dotenv()
    deps.TOKEN2 = getenv('TOKEN2')
    deps.TOKEN1 = getenv('TOKEN1')
    deps.TOKEN = deps.TOKEN2
    #deps.TOKEN = getenv('TOKEN')

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    deps.intents = Intents.default()
    deps.intents.members = True
    deps.intents.message_content = True
    deps.PREFIX = ['&', '& '] if deps.TOKEN == deps.TOKEN2 else ['!', '! ']
    # deps.PREFIX = ['!', '! ']
    deps.bot = Bot(command_prefix=deps.PREFIX, intents=deps.intents)

    deps.Country = cl.Country
    deps.Item = cl.Item
    deps.Market = cl.Market
    deps.Focus = cl.Focus
    deps.Factory = cl.Factory
    deps.ChooseMenu = cl.ChooseMenu
    deps.RpChannels = cl.RpChannels

async def second_config():
    """Присваивает остальным переменным их значения. Использовать функцию только после запуска"""
    deps.CHANNEL_FOR_UPDATE_ID = 1344823587093352569 
    deps.guild_id = 1344423355293372488
    deps.guild = deps.bot.get_guild(deps.guild_id)
    deps.game_state = {'game_started': True}
    deps.PAGE_SIZE = 25
    deps.CURRENCY = '£'
    deps.DATABASE_ROLE_PICKER_PATH = 'databases/role-picker.db'
    deps.DATABASE_COUNTRIES_PATH = 'databases/countries.db'
    deps.DATABASE_COUNTRY_AI_PATH = 'databases/country_ai.db'
    deps.DATABASE_FOCUS_PATH = 'databases/focuses.db'
    deps.DATABASE_CONFIG_PATH = 'databases/config.db'
    deps.RP_ROLES = {'COUNTRY': 1353608772458905671, 'surrender': 1361802354059378708, 
            'sea': 1357681946276266044, 'assambley': 1357679628243959862, 
            'LEAGUE': 1353894726847430766, 'gensec': 1358783484046348471, 
            'soviet': 1357679674410664076, 'PARAMS': 1358763645538009119,
            'registered': 1344519261216964710}
    deps.PERSONAL = {'politolog': deps.guild.get_role(1344824679390515280), 'mapper': deps.guild.get_role(1344824559777484861),
                        'moderator': deps.guild.get_role(1344824679390515280), 'anketolog': deps.guild.get_role(1344824637540012154),
                        'curator': deps.guild.get_role(1345434049027506187), 'zamcur': deps.guild.get_role(1345434049027506187),
                        'curpers': deps.guild.get_role(1344824766737027182),}
    deps.audit = deps.guild.get_channel(1454735211647733917) # #гарри text channelnnels()
    deps.rp_channels = deps.RpChannels()


