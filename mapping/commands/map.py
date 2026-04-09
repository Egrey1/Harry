from ..library import (
    Context,
    File,
    build_map_embed,
    build_map_stats,
    get_countries,
    hybrid_command,
    render_map_image,
)

class MapCommand:
    @hybrid_command(name='map')
    async def map(self, ctx: Context):
        countries = await get_countries()
        stats = build_map_stats(countries)
        image = render_map_image(countries)
        file = File(image, filename='map.png')

        description = (
            f"Свободно для регистрации: **{stats['free']}**\n"
            f"Всего стран: **{stats['total']}**\n"
            f"Занято стран: **{stats['busy']}**\n"
            f"Регионов на карте: **{stats['total_regions']}**"
        )

        if stats['surrendered']:
            description += f"\nКапитулировавших стран: **{stats['surrendered']}**"

        embed = build_map_embed(
            title='Политическая карта мира',
            description=description,
            image_name='map.png',
            color=0x3A5F8A,
        )
        embed.set_footer(text='Цвета и границы взяты из настроек стран')

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, file=file)
            return

        await ctx.send(embed=embed, file=file)
