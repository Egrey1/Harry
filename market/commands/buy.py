from ..library import Cog, Bot, hybrid_command, Context

class BuyCommand(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_buy", description="Покупка вооружения с рынка")
    async def add(self, ctx: Context):
        #Code here
        pass