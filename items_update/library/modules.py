from sqlite3 import connect as con
from sqlite3 import Row
from typing import List

import dependencies as deps

from discord.ext import tasks
from discord.ext.commands import Cog, Bot, command, Context