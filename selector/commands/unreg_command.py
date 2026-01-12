from ..library.modules import deps, Context, hybrid_command, Interaction

from ..library.functions import set_is_busy


class UnregCommand:
    def __init__(self):
        pass

    @hybrid_command(description='Снимает с вас регистрацию со страны')
    async def unreg(self, ctx: Context) -> None:
        country = deps.Country(ctx.author.mention)
        await ctx.interaction.response.defer(ephemeral=True)
        
        if country.busy is None:
            try:
                await ctx.send('Вы и так не страна!', ephemeral= True) # not country trying unreg
            except:
                await ctx.channel.send(f'{ctx.author.mention} Вы и так не страна!')
            return None

        await country.unreg()
        try:
            await ctx.send('Вы больше не страна!', ephemeral= True)
        except:
            await ctx.channel.send(f'{ctx.author.mention} Вы больше не страна!')
