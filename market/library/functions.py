from .modules import con, DATABASE_COUNTRIES, Row


async def give_items(country: str, item: str | None = None) -> dict[str, int] | int:
    connect = con(DATABASE_COUNTRIES)
    connect.row_factory = Row
    cursor = connect.cursor()

    if not item:
        cursor.execute(f"""
                        SELECT *
                        FROM countries_inventory
                        WHERE name = '{country}'
                        """)
        a = cursor.fetchone()
        connect.close()
        a = dict(a)
        items = {}

        for key, value in a.items():
            if key != "name":
                items[key] = int(value)

        return dict(items) if items else {}
    
    cursor.execute(f"""
                    SELECT `{item}`
                    FROM countries_inventory
                    WHERE name = '{country}'
                    """)
    item = cursor.fetchone()
    connect.close()
    return int(item[0]) if item else 0

async def country_positions(country: str) -> dict[str, str]:
    connect = con(DATABASE_COUNTRIES)
    connect.row_factory = Row
    cursor = connect.cursor()

    cursor.execute(f"""
                    SELECT *
                    FROM market
                    WHERE name = '{country}'
                    """)
    a = cursor.fetchone()
    connect.close()
    positions = {}
    a = dict(a)
    
    for key, value in a.items():
        if key != "name" and value and int(value.split()[0]):
            positions[key] = value
        
    return positions