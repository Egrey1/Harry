from .modules import con, DATABASE_PATH, Row

# Получаем все фабрики
async def give_all_factories() -> tuple:
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute("""
                SELECT name, cost, desc
                FROM factories
                """)
    result = cursor.fetchall()
    connect.close()
    return tuple(result)