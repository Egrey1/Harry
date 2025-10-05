from discord.ext.commands import Cog, Bot
from discord.ext.tasks import loop

from config import game_state, GUILD
from config import CHANNEL_FOR_UPDATE_ID as CHANNEL_ID

from re import match