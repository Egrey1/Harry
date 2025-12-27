from .loops import ChannelUpdate
from .library import Bot, Cog
    

class ChannelUpdaterCog(Cog, ChannelUpdate):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.update_channel.start()
    
    def cog_unload(self):
        self.update_channel.cancel()
    

async def setup(bot: Bot):
    await bot.add_cog(ChannelUpdaterCog(bot))