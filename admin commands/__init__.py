from .library.modules import Cog, Bot

from .commands.addCommand import AddCommand
from .commands.noSurrendCommand import NoSurrendCommand
from .commands.surrendCommand import SurrendCommand
from .commands.getInventoryCommand import GetInventoryCommand
from .commands.unregPlayerCommand import UnregPlayerCommand

class AdminCog(Cog, NoSurrendCommand, SurrendCommand, AddCommand, GetInventoryCommand, UnregPlayerCommand):
    def __init__(self, bot: Bot):
        self.bot = bot




async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
