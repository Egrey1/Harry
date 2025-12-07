from ..library.modules import con, deps, Row

async def have_sea(country: str) -> bool:
    from config import DATABASE_ROLE_PICKER as ROLE_PICKER_PATH
    connect = con(ROLE_PICKER_PATH)
    cursor = connect.cursor()

    cursor.execute(f"""
                   SELECT sea
                   FROM roles
                   WHERE name = '{country}'
                   """)
    result = cursor.fetchone()
    connect.close()

    return bool(result)

async def give_factories() -> tuple[dict[str, any], ...]:
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()


    cursor.execute(f"""
                SELECT *
                FROM country_factories
                """)
    a = cursor.fetchall()
    connect.close()

    result = []
    for i in a:
        result.append(dict(i)) 
    return result

async def to_items(factories_have: tuple[dict[str, any]]) -> tuple[dict[str, any]]:
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()


    cursor.execute(f"""
                    SELECT name, produces_key, count
                    FROM factories
                    """)
    # 
    a = cursor.fetchall()
    connect.close()
    result = []

    # Что производит и количество
    tmp = []
    for i in a:
        tmp.append(dict(i)) 
    a = tuple(tmp)

    for j in factories_have:
        b = {}
        b['name'] = j['name']
        for factory in a:
            if factory['produces_key'] != 'Деньги':
                b[factory['produces_key']] = factory['count'] * j[factory['name']]
        b['Деньги'] = a[-1]['count'] * j[a[-1]['name']] + a[-2]['count'] * j[a[-2]['name']]
        result.append(b)
        
    return tuple(result)

async def set_upd(coutry_items: tuple[dict[str, any]]) -> None:
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()

    for items in coutry_items:
        if not await have_sea(items['name']):
            ships = ['Подлодка', 'Эсминец', 'Крейсер', 'Линкор']
            for ship in ships:
                items[ship] = 0

        cursor.execute(f"""
                    INSERT OR REPLACE INTO countries_inventory_add ({', '.join(['\"' + i + '\"' for i in items.keys()])})
                    VALUES ({', '.join(['\"' + str(i) + '\"' for i in items.values()])})
                    """)
    connect.commit()
    connect.close()
    return None

async def give_items() -> tuple[dict[str, any], ...]:
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()


    cursor.execute(f"""
                    SELECT *
                    FROM countries_inventory_add
                    """)
    a = cursor.fetchall()


    connect.close()
    result = []
    for i in a:
        result.append(dict(i))
    return tuple(result)