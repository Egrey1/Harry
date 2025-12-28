from discord import Guild, Intents, TextChannel, ForumChannel
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
    
audit: TextChannel
    
class RpChannels:
    async def __init__(self, event: int | str | TextChannel = '📣┃события', war: int | str | TextChannel | ForumChannel = '🔥┃войны', news: int | str | TextChannel = '📰┃новости-стран'):
        """"""
        
    def get_event(self) -> TextChannel:
        """Возвращает канал для ивентов"""
    async def set_event(self, event: int | str | TextChannel = '📣┃события'):
        """Присвает полю self.event новое значение"""
    async def del_event(self):
        """Пересоздает канал ивента"""
        
    def get_war(self) -> ForumChannel:
        """Возвращает канал для войн"""
    async def set_war(self, event: int | str | ForumChannel = '🔥┃войны'):
        """Присвает полю self.war новое значение"""
    async def del_war(self):
        """Пересоздает канал войн"""
        
    def get_news(self) -> TextChannel:
        """Возвращает канал для новостей"""
    async def set_news(self, event: int | str | TextChannel = '📰┃новости-стран'):
        """Присвает полю self.news новое значение"""
    async def del_news(self):
        """Пересоздает канал новостей"""


rp_channels: RpChannels