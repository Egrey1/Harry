from ..library.modules import commands, Embed, CURRENCY
from ..library.functions import give_all_factories

from ..library.modules import (commands, Select, View, SelectOption,
                               CURRENCY, game_state)

from ..library.functions import give_all_factories

from ..library.callbacks.buyCallback import BuyCallback

class ShopCommand:
    def __init__(self):
        pass

    @commands.hybrid_command()
    async def shop(self, ctx: commands.Context) -> None:
        factories = await give_all_factories()
        embed_desc = ''

		# Добавляем все фабрики вместе с ценой и описанием
        for factory in factories:
            embed_desc += '### ' + factory[0] + ' - '+ CURRENCY + str(factory[1]) + '\n```' + factory[2] + '``` \n\n\n'
        
        embed = Embed(title='Все предприятия на продажу: ', description=embed_desc)

		# Выводим
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed= embed, ephemeral= True)
            return None
        await ctx.send(embed=embed)

    #Buy command is here
    @commands.hybrid_command(name='buy', description='Купить фабрику')
    async def buy(self, ctx: commands.Context):
        if not game_state['game_started']:
            return
        options = []

        # Добавляем в список все фабрики
        for factory in await give_all_factories():
            options.append(SelectOption(label=factory[0] + ' - ' + CURRENCY + str(factory[1]), value=factory[0]))
        
        view = View()
        select = Select(placeholder='Выберите предмет для покупки', options=options)
        select.callback = self.buy_callback
        view.add_item(select)

        if ctx.interaction:
            await ctx.interaction.response.send_message('Здесь вы можете купить что угодно, но только тс-с-с, никто не должен знать', view= view, ephemeral= True)
        else:
            await ctx.send('Здесь вы можете купить что угодно', view=view)    
