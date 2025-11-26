from ..library.modules import hybrid_command, describe, Context, Member

class KillCommand:
    def __init__(self):
        pass

    @hybrid_command(name='kill', description='Вы хотите кого-то убить?')
    @describe(deadboy='Это ваша жертва, необязательно что boy')
    async def kill(self, ctx: Context, deadboy: Member):
        await ctx.reply(f'{ctx.author.mention} killed 🔪 {deadboy.mention} 💀\nА на меня не смотрите, я тут непричём, я лишь озвучил это чуть ли не на весь сервер')