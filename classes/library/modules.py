from discord import Interaction, Member, TextChannel, Role
from discord.ext.commands import Context

from sqlite3 import connect as con
from sqlite3 import Row

from config import RP_ROLES as roles_id
from config import DATABASE_COUNTRIES as DATABASE_PATH
from config import DATABASE_ROLE_PICKER as ROLE_PICKER_PATH
from config import guild
from main import bot

from functions import *