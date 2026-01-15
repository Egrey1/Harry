from ..library import hybrid_command, has_permissions, Context, describe, Member, deps

class UnregPlayerCommand:
    @hybrid_command(name= 'unreg_player', description='Снимите регистрацию со страны')
    @has_permissions(administrator= True)
    @describe(member= 'Обязательно указать страну')
    async def unreg_player(self, ctx: Context, member: Member):
        if not ctx.interaction:
            await ctx.send('Правильнее будет /unreg_player @страна', ephemeral= True)
            return
        
        await ctx.interaction.response.defer(ephemeral= True)
        country = deps.Country(member.mention)
        if not country.busy:
            await ctx.interaction.followup.send('Мать моя богиня! Это же не страна, ты чего? Не буду я его снимать!', ephemeral= True)
            return
        
        await country.unreg()
        
        await ctx.interaction.followup.send('Он больше не страна!', ephemeral= True)
        
