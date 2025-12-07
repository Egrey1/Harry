from .modules import con, deps, Row


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

# chat GPT helped write this function
async def market_summary() -> dict[str, dict]:
    """Собирает сводку по рынку из таблицы `market`.

    Возвращает словарь вида:
    {
      'ItemName': {
          'total': int,  # общее количество на рынке по всем странам
          'sellers': [ {'country': str, 'price': int, 'qty': int}, ... ]
      },
      ...
    }

    Игнорирует пустые/нулевые ячейки.
    """
    connect = con(DATABASE_COUNTRIES)
    connect.row_factory = Row
    cursor = connect.cursor()

    cursor.execute("""
                   SELECT * 
                   FROM market
                   """)
    rows = cursor.fetchall()
    connect.close()

    summary: dict[str, dict] = {}

    for row in rows:
        r = dict(row)
        country = r.get('name')
        for key, value in r.items():
            if key == 'name' or not value:
                continue
            # value expected as "qty price"
            try:
                qty_str, price_str = str(value).split()
                qty = int(qty_str)
                price = int(price_str)
            except Exception:
                # skip malformed values
                continue

            if qty <= 0:
                continue

            if key not in summary:
                summary[key] = {'total': 0, 'sellers': []}

            summary[key]['total'] += qty
            summary[key]['sellers'].append({'country': country, 'price': price, 'qty': qty})

    return summary

async def country_money(country: str) -> int:
    connect = con(DATABASE_COUNTRIES)
    cursor = connect.cursor()

    cursor.execute(f"""
                    SELECT Деньги
                    FROM countries_inventory
                    WHERE name = '{country}'
                    """)
    money = cursor.fetchone()
    connect.close()
    return int(money[0]) if money else 0