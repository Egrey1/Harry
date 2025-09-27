from discord.ext.commands import Bot, Cog, hybrid_command, has_permissions, Context
from os import name
from sys import executable, argv
from subprocess import Popen

class OsCommands(Cog):
    def __init__(self, bot : Bot):
        self.bot = bot
    
    @hybrid_command(name='restart', description='Перезагрузка бота. Обновляет его код')
    @has_permissions(administrator= True)
    async def restart(self, ctx: Context):
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral= True)
        else:
            await ctx.send("Перезапуск бота...")
        
        # Запускаем новый процесс перед закрытием текущего
        try:  # Windows
            from subprocess import CREATE_NEW_CONSOLE
            Popen([executable] + argv, 
                            creationflags= CREATE_NEW_CONSOLE)
        except:  # Linux/Mac
            Popen([executable] + argv, start_new_session=True)
        
        # Корректно закрываем бота
        await self.bot.close()



async def setup(bot: Bot):
    await bot.add_cog(OsCommands(bot))