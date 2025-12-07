from discord import Member, Guild
from discord.ext.commands import hybrid_command, has_permissions, Context, Cog, Bot

import dependencies as deps

from sqlite3 import connect as con