from .library import Cog, Bot
from .commands import KillCommand

class RoflCommandsCog(Cog, KillCommand):
    def __init__(self, bot : Bot):
        self.bot = bot
    
    
    
async def setup(bot: Bot):
    await bot.add_cog(RoflCommandsCog(bot))