from ..library.modules import con, deps, Row

async def have_sea(country: str) -> bool:
    connect = con(deps.DATABASE_ROLE_PICKER_PATH)
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
    connect = con(deps.DATABASE_COUNTRIES_PATH)
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
    connect = con(deps.DATABASE_COUNTRIES_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()

    cursor.execute(f"""
                    SELECT name, produces_key, count
                    FROM factories
                    """)
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
                # Получаем количество этой фабрики у страны
                quantity = j.get(factory['name'], 0)
                
                # Рассчитываем производство с учетом убывающей отдачи
                total_production = 0
                for i in range(int(quantity)):
                    # i-я фабрика производит: базовое_значение × 0.95^i
                    factory_production = factory['count'] * (deps.diminishing_returns ** i)
                    total_production += factory_production
                
                b[factory['produces_key']] = total_production
        
        # Рассчитываем деньги (они производятся двумя последними фабриками)
        total_money = 0
        # Обе последние фабрики производят деньги
        for money_factory in [a[-2], a[-1]]:
            qty = j.get(money_factory['name'], 0)
            for i in range(int(qty)):
                total_money += money_factory['count'] * (deps.diminishing_returns ** i)
        
        b['Деньги'] = total_money
        result.append(b)
        
    return tuple(result)

async def set_upd(coutry_items: tuple[dict[str, any]]) -> None:
    connect = con(deps.DATABASE_COUNTRIES_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()

    for items in coutry_items:
        if not await have_sea(items['name']):
            ships = ['Подлодка', 'Эсминец', 'Крейсер', 'Линкор']
            for ship in ships:
                items[ship] = 0

        ebuchibothost1 = ', '.join(['\"' + i + '\"' for i in items.keys()])
        ebuchibothost2 = ', '.join(['\"' + str(i) + '\"' for i in items.values()])
        cursor.execute(f"""
                    INSERT OR REPLACE INTO countries_inventory_add ({ebuchibothost1})
                    VALUES ({ebuchibothost2})
                    """)
    connect.commit()
    connect.close()
    return None

async def give_items() -> tuple[dict[str, any], ...]:
    connect = con(deps.DATABASE_COUNTRIES_PATH)
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