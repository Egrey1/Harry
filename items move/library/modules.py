from discord import Interaction, Member, SelectOption
from discord.ui import Modal, View, Select, TextInput
from discord.ext.commands import hybrid_command, Context, Bot, Cog
from discord.app_commands import describe

from config import get_inventory, game_state, give_country
from config import DATABASE_COUNTRIES as DATABASE_PATH

from sqlite3 import connect as con