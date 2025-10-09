#from ..library.modules import (commands, Select, View, SelectOption,
#                               CURRENCY, game_state)

#from ..library.functions import give_all_factories

#from ..library.callbacks.buyCallback import BuyCallback

#class BuyCommand(BuyCallback):
#    def __init__(self):
#        pass

#    @commands.hybrid_command(name='buy', description='Купить фабрику')
#    async def buy(self, ctx: commands.Context):
#        if not game_state['game_started']:
#            return
#        options = []

        # Добавляем в список все фабрики
#        for factory in await give_all_factories():
#            options.append(SelectOption(label=factory[0] + ' - ' + CURRENCY + str(factory[1]), value=factory[0]))
        
#        view = View()
#        select = Select(placeholder='Выберите предмет для покупки', options=options)
#        select.callback = self.buy_callback
#        view.add_item(select)

#        if ctx.interaction:
#            await ctx.interaction.response.send_message('Здесь вы можете купить что угодно, но только тс-с-с, никто не должен знать', view= view, ephemeral= True)
#        else:
#            await ctx.send('Здесь вы можете купить что угодно', view=view)

