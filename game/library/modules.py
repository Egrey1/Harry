from discord import Member, Guild, Message, SelectOption, Interaction, Embed
from discord.ext.commands import hybrid_command, has_permissions, Context, Cog, Bot
from discord.ui import View, Select, Button, button

import dependencies as deps

from sqlite3 import connect as con