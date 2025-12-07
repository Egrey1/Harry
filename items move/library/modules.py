from discord import Interaction, Member, SelectOption
from discord.ui import Modal, View, Select, TextInput
from discord.ext.commands import hybrid_command, Context, Bot, Cog
from discord.app_commands import describe

import dependencies as deps

from sqlite3 import connect as con