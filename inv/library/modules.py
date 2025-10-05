from discord import Interaction, Embed
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discord.ui import View, Button


from sqlite3 import connect as con
from sqlite3 import Row

from config import DATABASE_COUNTRIES as DATABASE_COUNTRIES_PATH
from config import DATABASE_ROLE_PICKER as DATABASE_ROLE_PICKER_PATH
from config import give_country, CURRENCY, get_money