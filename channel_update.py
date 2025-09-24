from discord.ext import commands, tasks
from config import CHANNEL_FOR_UPDATE_ID as CHANNEL_ID
from config import GUILD, game_started

    

class ChannelUpdaterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_channel.start()
    
    def cog_unload(self):
        self.update_channel.cancel()

    async def increment_iteration(self, text: str) -> str:
        import re
        pattern = r'(.*?)(\d+)/(\d+)\s+(\d+)(.*)'
        match = re.match(pattern, text)
        
        if not match:
            return text
        
        prefix, current_str, total_str, year_str, suffix = match.groups()
        current = int(current_str)
        total = int(total_str)
        year = int(year_str)
        
        current += 1
        if current > total:
            current = 1
            year += 1
        
        return f"{prefix}{current}/{total} {year}{suffix}"

    @tasks.loop(hours=1)
    # @tasks.loop(seconds=10) # for test
    async def update_channel(self):
        if not game_started:
            return
        
        print('Бзиньк')
        guild = self.bot.get_guild(GUILD)
        channel = guild.get_channel(CHANNEL_ID)
        await channel.edit(name= await self.increment_iteration(channel.name))


    async def send_i_do(self):
        await self.bot.wait_until_ready()
        print('Выполняется')
    @update_channel.before_loop(send_i_do)
    async def pass_module(self):
        pass
        


        

async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelUpdaterCog(bot))