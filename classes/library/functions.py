from .modules import con, Row, DATABASE_PATH, Dict, Tuple, List, SelectOption, PAGE_SIZE
from ..game_objects import Item, Country, Factory

def get_options(values: Dict[str, str], page: int = 1) -> Tuple[List[SelectOption], int]:
    """
    Возвращает список SelectOption для указанной страницы.
    
    :param values: Словарь значений для SelectOption
    :param page: Номер страницы (начинается с 1)
    :return: Список SelectOption размером до PAGE_SIZE
    :return: Количество страниц
    """
    if not values:
        return [], 0  # Защита от пустоты
    
    keys = list(values.keys())

    page_size = PAGE_SIZE
    total_pages = (len(keys) + page_size - 1) // page_size  # ceil division

    # Ограничиваем page допустимым диапазоном
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    # Вычисляем срез
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page = keys[start_index:end_index]

    # Создаём SelectOption
    options = []
    for key in current_page:
        options.append(
            SelectOption(
                label= key,  
                value= values[key]
            )
        )

    return options, total_pages

def getbalance(country: str | Country) -> int:
    name = country.name if type(country) == Country else country
    
    connect = con(DATABASE_PATH)
    cursor = connect.cursor()
    
    cursor.execute(f"""
                    SELECT Деньги
                    FROM market
                    WHERE name = '{name}'
    """)
    res = cursor.fetchone()[0]
    connect.close()
    
    return int(res)

def getfact(country: str | Country, give_factory: str | Factory | None = None) -> dict[str: Factory] | Factory:
    name = country.name if type(country) == Country else country
    
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    
    res = {}
    cursor.execute(f"""
                    SELECT *
                    FROM country_factories
                    WHERE name = '{name}'
    """)
    fetch = dict(cursor.fetchone())
    connect.close()
    
    for factory_name, quantity in fetch.items():
        if factory_name != 'name':
            res[factory_name] = Factory(factory_name, quantity)
    
    if give_factory:
        return res[give_factory.name if type(give_factory) == Factory else give_factory]
    return res

def getinv(name: str | Country, give_item: str | Item | None = None) -> dict[str: Item] | Item:
    name = name.name if type(name) == Country else name
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    
    cursor.execute(f"""
                    SELECT *
                    FROM countries_inventory
                    WHERE name = '{name}'
    """)
    fetch = dict(cursor.fetchone())
    connect.close()
    res = {}
    for item_name, item_qnty in fetch.items():
        if item_name not in ['name', 'Деньги']:
            res[item_name] = Item(item_name, int(item_qnty))
    
    if not give_item:
        return res
    return res[give_item.name if type(give_item) == Item else give_item]