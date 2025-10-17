from .commands import *
from .library import Cog, Bot

class MarketCommands(Cog, AddCommand, EditCommand):
    def __init__(self, bot: Bot):
        self.bot = bot

async def setup(bot: Bot):
    await bot.add_cog(MarketCommands(bot))