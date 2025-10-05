from discord import Member, Guild
from discord.ext.commands import hybrid_command, has_permissions, Context, Cog, Bot

from config import RP_ROLES as roles_id
from config import DATABASE_COUNTRIES, DATABASE_ROLE_PICKER
from config import game_state, GUILD

from sqlite3 import connect as con