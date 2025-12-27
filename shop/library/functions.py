from .modules import con, Row, deps

# Получаем все фабрики
async def give_all_factories() -> tuple:
    connect = con(deps.DATABASE_COUNTRIES_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute("""
                SELECT name, cost, desc
                FROM factories
                """)
    result = cursor.fetchall()
    connect.close()
    return tuple(result)

