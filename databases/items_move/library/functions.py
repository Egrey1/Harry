"""Helper functions for moving/removing items using game objects only.

All DB mutations are done through the existing `Item.edit_quantity` method so
this module does not contain raw SQL.
"""
from typing import Tuple
import dependencies as deps


async def transfer_item(item_name: str, quantity: int, country_from: deps.Country, country_to: deps.Country) -> Tuple[int, int]:
    """Transfer `quantity` of `item_name` from `country_from` to `country_to`.

    Returns a tuple (left_in_from, new_amount_in_to).
    Raises ValueError on invalid input.
    """
    if quantity <= 0:
        raise ValueError('Количество должно быть положительным')

    item_from: deps.Item = country_from.inventory.get(item_name)
    if not item_from or item_from.quantity <= 0:
        raise ValueError('У отправителя нет такого предмета')

    to_transfer = min(quantity, item_from.quantity)

    # Decrease from sender
    new_from_qty = item_from.quantity - to_transfer
    item_from.edit_quantity(new_from_qty, country_from)
    item_from.quantity = new_from_qty

    # Increase recipient
    item_to: deps.Item = country_to.inventory.get(item_name)
    if item_to:
        new_to_qty = item_to.quantity + to_transfer
        item_to.edit_quantity(new_to_qty, country_to)
        item_to.quantity = new_to_qty
    else:
        # Create a new Item instance for recipient and persist
        new_item = deps.Item(item_name, quantity=to_transfer, country=country_to)
        new_item.edit_quantity(to_transfer, country_to)
        country_to.inventory[item_name] = new_item
        new_to_qty = to_transfer

    return new_from_qty, new_to_qty


async def remove_item(item_name: str, quantity: int, country: deps.Country) -> int:
    """Remove (consume) `quantity` of `item_name` from `country`.

    Returns the remaining amount after removal.
    """
    if quantity <= 0:
        raise ValueError('Количество должно быть положительным')

    item: deps.Item = country.inventory.get(item_name)
    if not item or item.quantity <= 0:
        raise ValueError('У страны нет такого предмета')

    to_remove = min(quantity, item.quantity)
    new_qty = item.quantity - to_remove
    item.edit_quantity(new_qty, country)
    item.quantity = new_qty
    return new_qty