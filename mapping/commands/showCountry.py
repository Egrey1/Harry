from ..library import hybrid_command, Context

class ShowCountryCommand:
    @hybrid_command(name='show_country')
    async def showcountry(self, ctx: Context):
        pass