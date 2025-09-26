# main.py
from discord.ext import commands
from config import TOKEN, PREFIX, intents

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

async def load_extensions():
    await bot.load_extension('selector')
    await bot.load_extension('inv')
    await bot.load_extension('shop')
    await bot.load_extension('items_move')
    await bot.load_extension('items_update')
    await bot.load_extension('channel_update')
    await bot.load_extension('game')
    await bot.load_extension('admin_commands')
    await bot.load_extension('os_commands')




@bot.event
async def on_ready():
    await load_extensions()
    await bot.tree.sync()
    print(f'Бот {bot.user} успешно запущен!')
    print(f'ID бота: {bot.user.id}') 
    print('------')



if __name__ == "__main__":
    bot.run(TOKEN)
    


     