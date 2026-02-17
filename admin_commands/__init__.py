from .library.modules import Cog, Bot

from .commands import *

class AdminCog(Cog, NoSurrendCommand, SurrendCommand, AddCommand, GetInventoryCommand, UnregPlayerCommand, ChangeNicknameCommand, DelCooldownCommand1):
    def __init__(self, bot: Bot):
        self.bot = bot




async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
