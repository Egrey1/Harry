from ..library.functions import give_all_factories
from ..library.modules import (commands, Embed, Select, View, SelectOption, deps)

from ..library.callbacks.buyCallback import BuyCallback

class ShopCommand(BuyCallback):
    def __init__(self):
        pass

    @commands.hybrid_command()
    async def shop(self, ctx: commands.Context) -> None:
        factories = await give_all_factories() # А вот не буду менять, надоело мне, пусть кто-то другой делает! АААAA
        embed_desc = ''

		# Добавляем все фабрики вместе с ценой и описанием
        for factory in factories:
            embed_desc += '### ' + factory[0] + ' - '+ deps.CURRENCY + str(factory[1]) + '\n```' + factory[2] + '\n\n' + f'Расходы - {deps.CURRENCY}{int(factory[3])} за единицу времени' '``` \n\n\n'
        
        embed = Embed(title='Все предприятия на продажу: ', description=embed_desc)
        view = View()
        options = []
        for factory in await give_all_factories():
            options.append(SelectOption(label=factory[0] + ' - ' + deps.CURRENCY + str(factory[1]), value=factory[0]))
        select = Select(placeholder='Выберите предмет для покупки', options=options)
        select.callback = self.buy_callback

        view.add_item(select)
		# Выводим
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed= embed, ephemeral=True, view= view)
            return None
        await ctx.send(embed=embed, view= view)

    