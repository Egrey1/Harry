from ..library import Cog, Bot, hybrid_command, Context

class EditCommand(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @hybrid_command(name="market_edit", description="Редактирует одну из ваших позиций на рынке")
    async def add(self, ctx: Context):
        #Code here
        pass