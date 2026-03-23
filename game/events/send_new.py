from ..library import Cog, Message, deps, Thread, logging
from ..views import CountryNewView

class NewEvent():
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_message(self, message: Message):
        if (
            (message.author.bot) or not 
            isinstance(message.channel, Thread) or 
            (message.channel.parent_id != (await deps.rp_channels.get_news()).id)):
            return
            
        
        country = deps.Country(message.author.mention)
        if not country.is_country:
            logging.info('Это не страна')
            await message.delete()
            await message.channel.send('Ты не страна!', delete_after=5)
            return
        
        country = deps.Country(message.author.mention)

        if message.channel.id != country.thread_id:
            logging.info('Попытка писать в чужом потоке')
            await message.delete()
            thread = deps.guild.get_thread(country.thread_id)
            await message.channel.send('Это не твой форум! ' + f'Твой поток находится здесь -> {thread.jump_url}' if thread else '', delete_after=30)
        
        if not message.attachments:
            logging.info('Нет файлов')
            await message.delete()
            await message.channel.send(content='Для отправки новости вы должны прикрепить хотя бы один медиафайл', delete_after=30)
            return
            
        if len(message.content.split()) < 25:
            logging.info('Мало слов')
            await message.channel.send(content='Твоя новость слишком маленького размера. Она должна иметь примерно 25 слов, чуть больше или чуть меньше', delete_after=30)
            await message.delete()
            return
            
        view = CountryNewView(country)

        await country.send_news(message.content, message.attachments, view= view)
        await message.delete()
        


