from .library import Cog, Bot
from .commands import *

class InventoryCog(Cog, InvCommand, BalCommand, RemFactCommand):
    def __init__(self, bot: Bot):
        self.bot = bot
        

async def setup(bot: Bot):
    await bot.add_cog(InventoryCog(bot))