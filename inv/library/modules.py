from discord import Interaction, Embed
from discord.ext import commands
from discord.ext.commands import Bot, Cog, hybrid_command, Context
from discord.ui import View, Button


from sqlite3 import connect as con
from sqlite3 import Row


import dependencies as deps