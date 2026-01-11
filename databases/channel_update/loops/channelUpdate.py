from ..library import Bot, deps, loop
from ..library import increment_iteration

class ChannelUpdate:
    def __init__(self, bot: Bot):
        self.bot = bot

    @loop(hours=deps.SPEED)
    # @loop(seconds=10) # for test
    async def update_channel(self):
        if not deps.game_state['game_started']:
            return
        
        print('Бзиньк')
        channel = deps.guild.get_channel(deps.CHANNEL_FOR_UPDATE_ID)
        await channel.edit(name= await increment_iteration(channel.name))