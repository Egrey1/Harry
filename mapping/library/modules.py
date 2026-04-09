from io import BytesIO
from os.path import exists, join
from typing import Iterable

from discord import Embed, File, Interaction, app_commands
from discord.app_commands import describe
from discord.ext.commands import Cog, Context, hybrid_command
from PIL import Image, ImageColor, ImageDraw

import dependencies as deps


def _open_map_background() -> Image.Image:
    for filename in ("map_background.png", "background.png"):
        path = join(deps.ASSETS_PATH, filename)
        if exists(path):
            return Image.open(path).convert("RGBA")
    raise FileNotFoundError("Map background image was not found in assets/")


def _parse_color(value: str | None, fallback: str) -> tuple[int, int, int, int]:
    color = value or fallback
    try:
        return ImageColor.getcolor(color, "RGBA")
    except ValueError:
        return ImageColor.getcolor(fallback, "RGBA")


def _adjust_color(
    color: tuple[int, int, int, int],
    *,
    brightness: float = 1.0,
    alpha_multiplier: float = 1.0,
) -> tuple[int, int, int, int]:
    r, g, b, a = color
    return (
        max(0, min(255, int(r * brightness))),
        max(0, min(255, int(g * brightness))),
        max(0, min(255, int(b * brightness))),
        max(0, min(255, int(a * alpha_multiplier))),
    )


def _iter_country_polygons(country: deps.Country) -> Iterable[list[tuple[int, int]]]:
    for state in country.states:
        if getattr(state, "cords", None):
            yield [(int(x), int(y)) for x, y in state.cords]


def _iter_country_state_polygons(country: deps.Country) -> Iterable[tuple[deps.State, list[tuple[int, int]]]]:
    for state in country.states:
        if getattr(state, "cords", None):
            yield state, [(int(x), int(y)) for x, y in state.cords]


def _normalize_edge(start: tuple[int, int], end: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    return (start, end) if start <= end else (end, start)


def _collect_border_edges(countries: list[deps.Country]) -> dict[
    tuple[tuple[int, int], tuple[int, int]],
    dict[str, object],
]:
    edge_map: dict[tuple[tuple[int, int], tuple[int, int]], dict[str, object]] = {}

    for country in countries:
        for state, polygon in _iter_country_state_polygons(country):
            if len(polygon) < 2:
                continue

            points = polygon + [polygon[0]]
            for index in range(len(points) - 1):
                start = points[index]
                end = points[index + 1]
                edge_key = _normalize_edge(start, end)

                if edge_key not in edge_map:
                    edge_map[edge_key] = {
                        "owners": set(),
                        "countries": [],
                        "count": 0,
                    }

                edge_map[edge_key]["owners"].add(country.id)
                edge_map[edge_key]["countries"].append(country)
                edge_map[edge_key]["count"] += 1

    return edge_map


def _get_country_bbox(country: deps.Country) -> tuple[int, int, int, int] | None:
    points: list[tuple[int, int]] = []
    for polygon in _iter_country_polygons(country):
        points.extend(polygon)

    if not points:
        return None

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


async def get_countries() -> list[deps.Country]:
    return await deps.Country.all()


def build_map_embed(
    *,
    title: str,
    description: str,
    image_name: str,
    color: int = 0x2B2D31,
) -> Embed:
    embed = Embed(title=title, description=description, color=color)
    embed.set_image(url=f"attachment://{image_name}")
    return embed


def render_map_image(
    countries: list[deps.Country],
    *,
    highlight_country: deps.Country | None = None,
) -> BytesIO:
    background = _open_map_background()
    image = background.copy()
    draw = ImageDraw.Draw(image, "RGBA")

    for country in countries:
        fill_color = _parse_color(getattr(country, "color", None), "#000000B0")

        if highlight_country is None:
            current_fill = fill_color
        elif country.id == highlight_country.id:
            current_fill = _adjust_color(fill_color, brightness=1.22, alpha_multiplier=1.0)
        else:
            current_fill = _adjust_color(fill_color, brightness=0.52, alpha_multiplier=0.55)

        for polygon in _iter_country_polygons(country):
            draw.polygon(polygon, fill=current_fill)

    edge_map = _collect_border_edges(countries)
    for edge, edge_info in edge_map.items():
        owners = edge_info["owners"]
        countries_on_edge: list[deps.Country] = edge_info["countries"]
        count = edge_info["count"]

        # Внутренние границы между регионами одной страны скрываем почти полностью.
        if len(owners) == 1 and count > 1:
            continue

        primary_country = countries_on_edge[0]
        border_color = _parse_color(getattr(primary_country, "border", None), "#000000")

        if highlight_country is not None and any(country.id == highlight_country.id for country in countries_on_edge):
            line_color = _adjust_color(border_color, brightness=1.35, alpha_multiplier=1.0)
            line_width = 4
        elif len(owners) > 1:
            line_color = _adjust_color(border_color, brightness=1.15, alpha_multiplier=0.95)
            line_width = 3
        else:
            # Внешний контур страны или береговая линия.
            line_color = _adjust_color(border_color, brightness=1.0, alpha_multiplier=0.65)
            line_width = 2

        draw.line(edge, fill=line_color, width=line_width)

    if highlight_country is not None:
        bbox = _get_country_bbox(highlight_country)
        if bbox is not None:
            min_x, min_y, max_x, max_y = bbox
            width = max_x - min_x
            height = max_y - min_y
            padding = max(70, int(max(width, height) * 0.25))

            left = max(0, min_x - padding)
            top = max(0, min_y - padding)
            right = min(image.width, max_x + padding)
            bottom = min(image.height, max_y + padding)

            if right > left and bottom > top:
                cropped = image.crop((left, top, right, bottom))
                image = cropped.resize(background.size, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def build_map_stats(countries: list[deps.Country]) -> dict[str, int]:
    total = len(countries)
    busy = sum(1 for country in countries if getattr(country, "busy", None))
    free = sum(1 for country in countries if not getattr(country, "busy", None) and not getattr(country, "surrend", False))
    surrendered = sum(1 for country in countries if getattr(country, "surrend", False))
    total_regions = sum(len(country.states) for country in countries)
    return {
        "total": total,
        "busy": busy,
        "free": free,
        "surrendered": surrendered,
        "total_regions": total_regions,
    }
