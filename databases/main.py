import dependencies as deps
from config import first_config, second_config

async def load_extensions():
    await deps.bot.load_extension('rofl_commands')
    await deps.bot.load_extension('selector')
    await deps.bot.load_extension('inv')
    await deps.bot.load_extension('admin_commands')
    await deps.bot.load_extension('shop')
    await deps.bot.load_extension('items_move')
    await deps.bot.load_extension('items_update')
    await deps.bot.load_extension('channel_update')
    await deps.bot.load_extension('game')
    await deps.bot.load_extension('os_commands')
    await deps.bot.load_extension('market')


async def on_ready():
    print('Бот запускается!')
    await second_config()
    await load_extensions()
    await deps.bot.tree.sync()
    print(f'Бот {deps.bot.user} успешно запущен!')
    print(f'ID бота: {deps.bot.user.id}')
    print('------')


if __name__ == "__main__":
    first_config()
    deps.bot.add_listener(on_ready)
    deps.bot.run(deps.TOKEN)

# SkyDevTech inc <3

