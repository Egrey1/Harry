from .library.modules import Cog, Bot
from .commands import GiveCommand, UseCommand



class ItemsCog(Cog, GiveCommand, UseCommand):
    def __init__(self, bot: Bot):
        self.bot = bot
   

async def setup(bot: Bot):
    await bot.add_cog(ItemsCog(bot))