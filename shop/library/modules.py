from sqlite3 import connect as con
from sqlite3 import Row


from config import DATABASE_COUNTRIES as DATABASE_PATH
from config import CURRENCY, give_country, get_money, get_cost, game_state


from discord import Embed, Interaction, SelectOption
from discord.ext import commands
from discord.ext.commands import Cog, Bot

from discord.ui import Modal, Select, View, TextInput