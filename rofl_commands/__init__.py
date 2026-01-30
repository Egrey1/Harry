from .library import Cog, Bot
from .commands import KillCommand, Quote
from .events import FeedHarryEvent

class RoflCommandsCog(Cog, KillCommand, Quote, FeedHarryEvent):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    
    
async def setup(bot: Bot):
    await bot.add_cog(RoflCommandsCog(bot))