from .library.modules import Cog, Bot
from .commands import InvCommand, BalCommand

class InventoryCog(Cog, InvCommand, BalCommand):
    def __init__(self, bot: Bot):
        self.bot = bot
        

async def setup(bot: Bot):
    await bot.add_cog(InventoryCog(bot))