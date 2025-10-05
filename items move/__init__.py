from .library.modules import Cog, Bot



class ItemsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
   

async def setup(bot: Bot):
    await bot.add_cog(ItemsCog(bot))