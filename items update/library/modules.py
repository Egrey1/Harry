from sqlite3 import connect as con
from sqlite3 import Row

from config import DATABASE_COUNTRIES as DATABASE_PATH
from config import game_state

from discord.ext import tasks
from discord.ext.commands import Cog, Bot, command, Context