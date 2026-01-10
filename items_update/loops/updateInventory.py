from ..library.modules import tasks, con, deps
from ..library.functions import give_factories, to_items, set_upd, give_items


class UpdateInventory:
    def __init__(self):
        pass

    @tasks.loop(hours=1)
    # @tasks.loop(seconds=10) # for test
    async def update_inventories(self):
        if not deps.game_state['game_started']:
            return
        
        print('Инвентарь обновляется')
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        cursor = connect.cursor()


        inv_update = await give_items() #


        for country in inv_update:
            for item, count in country.items():
                if item != 'name' and count != 0:
                    cursor.execute(f"""
                                    UPDATE countries_inventory
                                    SET "{item}" = "{item}" + {float(count)}
                                    WHERE name = "{country['name']}"
                                    """)
        connect.commit()
        connect.close()

        factories = await give_factories()
        items = await to_items(factories)
        await set_upd(items)
