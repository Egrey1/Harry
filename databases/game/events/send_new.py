from ..library import Cog, Message, deps
from ..views import CountryNewView

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
        
        if not message.attachments:
            await message.channel.send(content='Для отправки новости вы должны прикрепить хотя бы один медиафайл', ephemeral=True)
            await message.delete()
            return
            
        if len(message.content.split(' ')) < 25:
            await message.channel.send(content='Твоя новость слишком маленького размера. Она должна иметь примерно 25 слов, чуть больше или чуть меньше', ephemeral=True)
            await message.delete()
            return
            
        view = CountryNewView(country)

        await country.send_news(message.content, message.attachments, view= view)
        await message.delete()
        


