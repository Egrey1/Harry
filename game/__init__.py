from .library import Cog, Bot, deps
from .commands import VipeCommand, FocusesCommand
from .loops import FocusesLoop
from .events import NewEvent

class GameCog(Cog, VipeCommand, FocusesCommand, FocusesLoop, NewEvent):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild = deps.guild
        self.focus_loop.start()
        
    def cog_unload(self):
        self.focus_loop.cancel()
    

async def setup(bot: Bot):
    await bot.add_cog(GameCog(bot))