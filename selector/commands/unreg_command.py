from ..library.modules import (commands, 
                             give_country, deps)

from ..library.functions import set_is_busy


class UnregCommand:
    def __init__(self):
        pass

    @commands.hybrid_command(description='Снимает с вас регистрацию со страны')
    async def unreg(self, ctx: commands.Context) -> None:
        country = deps.Country(ctx.author.mention)

        if country.busy is None:
            await ctx.send('Вы и так не страна!', ephemeral= True) # not country trying unreg
            return None

        country.unreg()
        await ctx.send('Вы больше не страна!', ephemeral= True)