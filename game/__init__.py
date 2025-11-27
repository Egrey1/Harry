from .library import Cog, Bot, GUILD
from .commands import VipeCommand

class GameCog(Cog, VipeCommand):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild = bot.get_guild(GUILD)
    

async def setup(bot: Bot):
    await bot.add_cog(GameCog(bot))