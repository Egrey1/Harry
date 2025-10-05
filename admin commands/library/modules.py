from discord import SelectOption, Interaction, TextInput
from discord.ui import View, Select, Modal
from discord.app_commands import describe
from discord.ext.commands import Cog, Bot, hybrid_command, has_permissions, Context

from config import give_country
from config import RP_ROLES as roles_id
from config import DATABASE_COUNTRIES as DATABASE_PATH
from config import DATABASE_ROLE_PICKER as ROLE_PICKER_PATH

from sqlite3 import connect as con
from sqlite3 import Row

