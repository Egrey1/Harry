from .library import Cog
from .commands import *

class MappingCog(Cog, MapCommand, ShowCountryCommand):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(MappingCog(bot))