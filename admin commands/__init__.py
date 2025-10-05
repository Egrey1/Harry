from .library.modules import Cog, Bot

from .commands.addCommand import AddCommand
from .commands.noSurrendCommand import NoSurrendCommand
from .commands.surrendCommand import SurrendCommand

class AdminCog(Cog, NoSurrendCommand, SurrendCommand, AddCommand):
    def __init__(self, bot: Bot):
        self.bot = bot




async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
