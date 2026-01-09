from ..library import Cog, Message, deps

class NewEvent(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot or message.channel.id != deps.rp_channels.get_news().id:
            return
        
        country = deps.Country(message.author.mention)
        if not country.is_country:
            return
        
        await country.send_news(message.content)
        await message.delete()
        


