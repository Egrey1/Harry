from .library.modules import Cog, Bot
from .commands.invCommand import InvCommand

class InventoryCog(Cog, InvCommand):
    def __init__(self, bot: Bot):
        self.bot = bot
        

async def setup(bot: Bot):
    await bot.add_cog(InventoryCog(bot))