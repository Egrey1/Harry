from sqlite3 import Row
from sqlite3 import connect as con

import dependencies as deps

from discord import Interaction, app_commands, SelectOption, Member
from discord.ext.commands import Bot, Cog
from discord.ext import commands
from discord.ui import View, Select