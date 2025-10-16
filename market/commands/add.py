from ..library import Cog, Bot, hybrid_command, Context, give_country

class AddCommand(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_add", description="Добавляет вашу позицию на рынок")
    async def add(self, ctx: Context):
        country = await give_country(ctx.author.mention)
        

        pass