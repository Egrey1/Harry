from ..library.modules import Bot, deps, loop
from ..library.functions import increment_iteration

class ChannelUpdate:
    def __init__(self, bot: Bot):
        self.bot = bot

    @loop(hours=1)
    # @loop(seconds=10) # for test
    async def update_channel(self):
        if not game_state['game_started']:
            return
        
        print('Бзиньк')
        guild = self.bot.get_guild(GUILD)
        channel = guild.get_channel(CHANNEL_ID)
        await channel.edit(name= await increment_iteration(channel.name))