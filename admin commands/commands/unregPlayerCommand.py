from ..library.modules import hybrid_command, has_permissions, Context, describe, Member, deps
from ..library.functions import unreg_function

class UnregPlayerCommand:
    @hybrid_command(name= 'unreg_player', description='Снимите регистрацию со страны')
    @has_permissions(administrator= True)
    @describe(member= 'Обязательно указать страну')
    async def unreg_player(self, ctx: Context, member: Member):
        if not ctx.interaction:
            await ctx.reply('/unreg_player правильнее будет')
            return

        country = Country(ctx.author.mention)
        if not country.busy:
            await ctx.send('Мать моя богиня! Это же не страна, ты чего? Не буду я его снимать!', ephemeral= True)
            return
        
        country.unreg()
        
        await ctx.send('Это больше не страна!', ephemeral= True)
        
