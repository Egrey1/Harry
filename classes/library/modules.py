from discord import Interaction, Member, TextChannel, Role, SelectOption, ButtonStyle, NotFound
from discord.ext.commands import Context
from discord.ui import View, Select, Button

from sqlite3 import connect as con
from sqlite3 import Row

from config import RP_ROLES as roles_id
from config import DATABASE_FOCUS as FOCUS_PATH
from config import DATABASE_COUNTRIES as DATABASE_PATH
from config import DATABASE_ROLE_PICKER as ROLE_PICKER_PATH
from config import guild, PAGE_SIZE, get_channel
from main import bot

from functions import *

from typing import Dict, Tuple, List, Callable, Awaitable

from asyncio import Lock