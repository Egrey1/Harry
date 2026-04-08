from ..library import hybrid_command, Context, deps, File, PIL

class MapCommand:
    @hybrid_command(name='map')
    async def map(self, ctx: Context):
        i = PIL.Image.open(deps.ASSETS_PATH + 'map_background.png')
        