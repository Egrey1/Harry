from .library import Cog, Bot, deps
from .commands import VipeCommand, FocusesCommand
from .loops import FocusesLoop, Autovipe, AILoop
from .events import NewEvent

class GameCog(Cog, VipeCommand, FocusesCommand, FocusesLoop, Autovipe, NewEvent, AILoop):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild = deps.guild
        self.focus_loop.start()
        self.autovipe.start()
        self.ai.start()
        
    def cog_unload(self):
        self.focus_loop.cancel()
        self.autovipe.cancel()
        self.ai.start()
    

async def setup(bot: Bot):
    await bot.add_cog(GameCog(bot))