from .library.modules import commands, Member, Bot, Cog
from .library.functions import set_is_busy

from .commands.reg_command import RegCoommand
from .commands.unreg_command import UnregCommand

    

class SelectorCog(Cog, RegCoommand, UnregCommand):
    def __init__(self, bot: Bot):
        self.bot = bot
    

    @Cog.listener()
    async def on_member_remove(self, user: Member):
        await set_is_busy(user.mention)



async def setup(bot: Bot):
    await bot.add_cog(SelectorCog(bot))