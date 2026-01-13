from discord.ext.commands import Cog, Bot, Context, hybrid_command
from discord import Interaction, SelectOption, Embed
from discord.ui import View, Select, TextInput, Modal
from typing import List, Dict

import dependencies as deps

from sqlite3 import connect as con
from sqlite3 import Row