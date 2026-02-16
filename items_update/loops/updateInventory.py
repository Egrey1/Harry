from ..library.modules import tasks, con, deps, List, Row
from ..library.functions import give_factories, to_items, set_upd, give_items
import logging


class UpdateInventory:
    def __init__(self):
        pass

    @tasks.loop(hours=deps.SPEED)
    # @tasks.loop(seconds=10) # for test
    async def update_inventories(self):
        if not deps.game_state['game_started']:
            return
        
        logging.info('Инвентарь обновляется')
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
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute(f"""
                       SELECT *
                       FROM countries_inventory
                       """)
        fetchs = cursor.fetchall()
        # countries: List[deps.Country] = []
        # for fetch in fetchs:
        #     countries.append(deps.Country(fetch['name']))

        total_money = 0
        current_country: deps.Country

        # цикл по всем странам
        for fetch in fetchs:
            current_country = deps.Country(fetch['name'])
            for factory in [list(current_country.factories.values())[-2], list(current_country.factories.values())[-1]]: # две последние фабрики производят деньги
                total_money += factory.count * factory.quantity

            # цикл по всем предметам в инвентаре страны
            for row in fetch.keys():
                if row in ('name', 'Деньги'):
                    continue

                factories = current_country.inventory[row].produced_by

                if factories is None:
                    print(f"Предмет {row} не производится фабриками, пропускаем...")

                # цикл по всем фабриками, что производят предмет с названием row
                for factory in factories:
                    total_money -= factory.maintenance * factory.quantity
                    no_fine_count = min(factory.quantity, factory.max_size)
                    if total_money >= 0:
                        cursor.execute(f"""
                                UPDATE countries_inventory_add
                                SET "{row}" = "{
                                    (no_fine_count * factory.count) + 
                                    factory.count * (1 - deps.diminishing_returns ** (factory.quantity - no_fine_count)) / 
                                    (1 - deps.diminishing_returns) }"
                                WHERE name = "{current_country.name}"
                                """)
            cursor.execute(f"""
                           UPDATE countries_inventory_add
                           SET "Деньги" = "{total_money}"
                           WHERE name = "{current_country.name}"
                           """)

        connect.commit()
        connect.close()

        



        # factories = await give_factories()
        # items = await to_items(factories)
        # await set_upd(items)
