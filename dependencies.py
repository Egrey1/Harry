from discord import Guild, Intents
from discord.ext.commands import Bot
from classes import *

bot: Bot
DATABASE_ROLE_PICKER_PATH: str
DATABASE_COUNTRIES_PATH: str
DATABASE_FOCUS_PATH: str
DATABASE_CONFIG_PATH: str

CURRENCY: str
RP_ROLES: dict

CHANNEL_FOR_UPDATE_ID: int
"""Канал, который будет обновляться каждую единицу времени"""

guild_id: int
"""Detrimentum"""
guild: Guild
"""Detrimentum"""

game_state: dict
PAGE_SIZE: int = 25

TOKEN: str
intents: Intents
PREFIX: str