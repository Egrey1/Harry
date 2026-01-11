from sqlite3 import connect as con
from sqlite3 import Row

import dependencies as deps

from discord import Embed, Interaction, SelectOption
from discord.ext import commands
from discord.ext.commands import Cog, Bot

from discord.ui import Modal, Select, View, TextInput