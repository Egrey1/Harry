from .library.modules import Cog, Bot

from .commands import BuyCommand, ShopCommand
#from .commands.shopCommand import ShopCommand


class ShopCog(Cog, BuyCommand, ShopCommand):
    def __init__(self, bot: Bot):
        self.bot = bot



async def setup(bot: Bot):
    await bot.add_cog(ShopCog(bot))