from .library import Bot, Cog
from .commands import RestartCommand

class OsCommands(Cog, RestartCommand):
    def __init__(self, bot : Bot):
        self.bot = bot
    
    
    
async def setup(bot: Bot):
    await bot.add_cog(OsCommands(bot))