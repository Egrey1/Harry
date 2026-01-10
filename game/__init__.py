from .library import Cog, Bot, deps
from .commands import VipeCommand, FocusesCommand

class GameCog(Cog, VipeCommand, FocusesCommand):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild = deps.guild
    

async def setup(bot: Bot):
    await bot.add_cog(GameCog(bot))