from ..library.modules import commands, Embed, CURRENCY
from ..library.functions import give_all_factories

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
