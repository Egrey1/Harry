from .library import Cog, Bot, command, Context
from .loops import UpdateInventory


    

class UpdaterCog(Cog, UpdateInventory):
    def __init__(self, bot : Bot):
        self.bot = bot
        self.update_inventories.start()
    
    def cog_unload(self):
        self.update_inventories.cancel()
    
    @command(name='collect')
    async def no_collect(self, ctx: Context):
        await ctx.reply('У нас нет этой команды! Деньги и армия обновляется автоматически!')


        

async def setup(bot: Bot):
    await bot.add_cog(UpdaterCog(bot))