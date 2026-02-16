from ..library.modules import con, deps, Row

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