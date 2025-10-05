from sqlite3 import Row
from sqlite3 import connect as con

from config import DATABASE_ROLE_PICKER as DATABASE_PATH
from config import RP_ROLES as roles_id
from config import give_country, game_state

from discord import Interaction, app_commands, SelectOption, Member
from discord.ext.commands import Bot, Cog
from discord.ext import commands
from discord.ui import View, Select