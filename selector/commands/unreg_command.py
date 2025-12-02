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
        await ctx.send('Вы больше не страна', ephemeral= True)

        # if ctx.interaction:
        #     await ctx.interaction.response.defer(ephemeral=True)
        # else:
        #     await ctx.send('Ожидайте снятия ролей, это не займет много времени')
        
        # country = await give_country(ctx.author.mention)
        # if not country:
        #     if ctx.interaction:
        #         await ctx.interaction.followup.send('Вы и так не были страной', ephemeral=True)
        #     return None

        # user = ctx.author
        # for id in deps.RP_ROLES.values():
        #     try:
        #         role = ctx.guild.get_role(id) 
        #         await user.remove_roles(role) 
        #     except:
        #         continue
        # try:
        #     unreg = ctx.guild.get_role(1344519330091503628)
        #     await user.add_roles(unreg)  
        #     try:
        #         await user.edit(nick='') 
        #     except:
        #         pass
        # except:
        #     pass
        
        # await set_is_busy(user.mention)


        # if ctx.interaction:
        #     await ctx.interaction.followup.send('Вы больше не страна', ephemeral=True)
        #     return None
        # await ctx.send('Вы больше не страна')