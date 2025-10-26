from ..library.modules import hybrid_command, has_permissions, Context, describe, Member, give_country
from ..library.functions import unreg_function

class UnregPlayerCommand:
    @hybrid_command(name= 'unreg_player', description='Снимите регистрацию со страны')
    @has_permissions(administrator= True)
    @describe(member= 'Обязательно указать страну')
    async def unreg_player(self, ctx: Context, member: Member):
        if not ctx.interaction:
            await ctx.reply('/unreg_player правильнее будет')
            return

        country = await give_country(ctx.author.mention)
        if not country:
            await ctx.reply('Мать моя богиня! Это же не страна, ты чего? Не буду я его снимать!', ephemeral= True)
            return
        
        await unreg_function(country, ctx.interaction)
        await ctx.reply('Это больше не страна!', ephemeral= True)
        
