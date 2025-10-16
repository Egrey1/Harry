from config import con, DATABASE_COUNTRIES

async def give_items(country: str, item: str | None = None) -> dict[str, int] | int:
    connect = con(DATABASE_COUNTRIES)
    cursor = connect.cursor()

    if not item:
        cursor.execute(f"""
                        SELECT *
                        FROM countries_inventory
                        WHERE name = '{country}'
                        """)
        items = cursor.fetchone()
        connect.close()
        return dict(items) if items else {}
    
    cursor.execute(f"""
                    SELECT `{item}`
                    FROM countries_inventory
                    WHERE name = '{country}'
                    """)
    item = cursor.fetchone()
    connect.close()
    return item[0] if item else 0