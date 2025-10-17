from discord.ext.commands import Cog, Bot, Context, hybrid_command
from discord import Interaction, SelectOption
from discord.ui import View, Select, TextInput, Modal

from config import give_country, DATABASE_COUNTRIES, CURRENCY

from sqlite3 import connect as con
from sqlite3 import Row