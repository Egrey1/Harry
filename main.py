from dependencies import bot, TOKEN
from config import first_config, second_config


async def load_extensions():
    await bot.load_extension('selector')
    await bot.load_extension('inv')
    await bot.load_extension('admin commands')
    await bot.load_extension('shop')
    await bot.load_extension('items move')
    await bot.load_extension('items update')
    await bot.load_extension('channel update')
    await bot.load_extension('game')
    await bot.load_extension('os commands')
    await bot.load_extension('rofl commands')
    await bot.load_extension('market') 



@bot.event
async def on_ready():
    print(f'Бот запускается!')
    second_config()
    await load_extensions()
    await bot.tree.sync()
    print(f'Бот {bot.user} успешно запущен!')
    print(f'ID бота: {bot.user.id}') 
    print('------')



if __name__ == "__main__":
    first_config()
    bot.run(TOKEN)
    