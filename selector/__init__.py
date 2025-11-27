from .library import commands, Member, Bot, Cog, set_is_busy

from .commands import RegCoommand, UnregCommand


    

class SelectorCog(Cog, RegCoommand, UnregCommand):
    def __init__(self, bot: Bot):
        self.bot = bot
    

    @Cog.listener()
    async def on_member_remove(self, user: Member):
        await set_is_busy(user.mention)



async def setup(bot: Bot):
    await bot.add_cog(SelectorCog(bot))