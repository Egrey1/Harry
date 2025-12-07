from .modules import con, deps

async def remove_item(item: str, quantity: int, country: str) -> int:
    connect = con(DATABASE_PATH)
    cursor = connect.cursor()
    if quantity < 0:
        raise ValueError('Число отрицательное')

    cursor.execute(f"""
                    SELECT {item}
                    FROM countries_inventory
                    WHERE name = '{country}'
                   """)
    quantity = min(quantity, int(cursor.fetchone()[0]))

    cursor.execute(f"""
                    UPDATE countries_inventory
                    SET {item} = {item} - '{quantity}'
                    WHERE name = '{country}'
                   """)
    connect.commit()

    cursor.execute(f"""
                    SELECT {item}
                    FROM countries_inventory
                    WHERE name = '{country}'
                   """)
    res = cursor.fetchone()[0]
    connect.close()
    
    return res