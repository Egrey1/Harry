from ..library import (
    Context,
    File,
    Interaction,
    app_commands,
    build_map_embed,
    build_map_stats,
    describe,
    deps,
    hybrid_command,
    render_map_image,
)


class ShowCountryCommand:
    async def _send_error(self, ctx: Context, text: str) -> None:
        if ctx.interaction:
            await ctx.interaction.response.send_message(text, ephemeral=True)
            return
        await ctx.send(text)

    @hybrid_command(name="show_country")
    @describe(country_name="Имя страны, которую нужно показать на карте")
    async def showcountry(self, ctx: Context, country_name: str | None = None):
        viewer_country = deps.Country(ctx.author.mention)
        target_name = country_name if country_name else viewer_country.name if viewer_country.is_country else None

        if target_name is None:
            await self._send_error(ctx, "Если ты не страна, имя страны для просмотра нужно указать явно.")
            return

        target_country = deps.Country(target_name)
        if not target_country.is_country:
            await self._send_error(ctx, "Такой страны я не нашел.")
            return

        if not target_country.states:
            await self._send_error(ctx, "У этой страны пока нет регионов на карте.")
            return

        countries = await deps.Country.all()
        stats = build_map_stats(countries)
        image = render_map_image(countries, highlight_country=target_country)
        file = File(image, filename="show_country.png")

        description = (
            f"Регионов у страны: **{len(target_country.states)}**\n"
            f"Свободно для регистрации стран: **{stats['free']}**\n"
            f"Всего стран в игре: **{stats['total']}**"
        )

        if target_country.busy:
            description += "\nСтатус: **занята игроком**"
        elif target_country.surrend:
            description += "\nСтатус: **капитулировала**"
        else:
            description += "\nСтатус: **свободна**"

        embed = build_map_embed(
            title=f"Карта страны {target_country.name}",
            description=description,
            image_name="show_country.png",
            color=0x4C7D52,
        )
        embed.set_footer(text="Выбранная страна выделена ярче и показана крупнее")

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, file=file)
            return

        await ctx.send(embed=embed, file=file)

    @showcountry.autocomplete("country_name")
    async def showcountry_autocomplete(self, interaction: Interaction, current: str):
        countries = await deps.Country.all()
        current_lower = current.lower()
        matches = [
            app_commands.Choice(name=country.name, value=country.name)
            for country in countries
            if current_lower in country.name.lower()
        ]
        return matches[:25]
