from .library import Cog

class MappingCog(Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(MappingCog(bot))