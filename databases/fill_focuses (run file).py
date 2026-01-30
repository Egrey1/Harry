from sqlite3 import connect

def get_all_focuses(focus_name, db_file: str = 'focuses.db', table: str = 'all_focuses'):
    if not focus_name:
        return {}
    con = connect(db_file)
    cursor = con.cursor()
    
    cursor.execute(f"""
        SELECT `name`
        FROM {table}
        WHERE after = ?
    """, (focus_name,))
    
    fetches = cursor.fetchall()
    con.close()
    
    all_names = {}
    
    # Получаем список прямых потомков
    direct_children = [fetch[0] for fetch in fetches]
    all_names[focus_name] = direct_children
    
    # Рекурсивно получаем все поддерево
    for child in direct_children:
        child_results = get_all_focuses(child, db_file, table)
        # Объединяем результаты
        all_names.update(child_results)
    
    return all_names

def fill_items():
    con = connect('countries.db')
    cursor = con.cursor()
    
    cursor.execute("""
        SELECT name
        FROM items
    """)
    fetches = cursor.fetchall()
    con.close()
    return [fetch[0] for fetch in fetches]

def fill_factories():
    con = connect('countries.db')
    cursor = con.cursor()
    
    cursor.execute("""
        SELECT name
        FROM factories
    """)
    fetches = cursor.fetchall()
    con.close()
    return [fetch[0] for fetch in fetches]

def fill_countries():
    con = connect('countries.db')
    cursor = con.cursor()
    
    cursor.execute("""
        SELECT name
        FROM countries_inventory
    """)
    fetches = cursor.fetchall()
    con.close()
    return [fetch[0] for fetch in fetches]

def format_requirements(items_list):
    """
    Форматирует требования в строку вида "item:число; item2:число"
    """
    if not items_list:
        return None
    
    result = []
    for item in items_list:
        if item['amount'] > 0:  # Добавляем только если количество > 0
            result.append(f"{item['name']}:{item['amount']}")
    
    if not result:
        return None
    
    return '; '.join(result)

def print_list_with_indexes(items_list, items_per_line=5):
    """Выводит список с нумерацией по несколько элементов в строке"""
    for i, item in enumerate(items_list):
        print(f'[{i:2}] {item:<40}', end=' ')
        if (i + 1) % items_per_line == 0:
            print()
    if len(items_list) % items_per_line != 0:
        print()

def get_selection_from_list(item_list, item_type, selection_type="выбрать"):
    """Получает выбор элементов из списка через индексы"""
    if not item_list:
        print(f"Список {item_type} пуст!")
        return []
    
    selected_items = []
    print(f"\n=== {item_type.capitalize()} (выбор через индексы) ===")
    print_list_with_indexes(item_list)
    
    while True:
        try:
            choice_input = input(f'\nВведите номер {item_type} для добавления '
                               f'(или несколько через пробел, или "г" для завершения): ')
            
            if choice_input.lower() == 'г':
                break
            
            if not choice_input.strip():
                continue
            
            # Обработка нескольких номеров через пробел
            indexes = [int(idx.strip()) for idx in choice_input.split()]
            
            for idx in indexes:
                if 0 <= idx < len(item_list):
                    selected_name = item_list[idx]
                    
                    # Проверяем, не выбран ли уже этот элемент
                    if selected_name in [item['name'] for item in selected_items]:
                        print(f"⚠ {item_type[:-1]} '{selected_name}' уже выбран!")
                        continue
                    
                    try:
                        amount = int(input(f'Количество для "{selected_name}": '))
                        if amount > 0:
                            selected_items.append({'name': selected_name, 'amount': amount})
                        else:
                            print("❌ Количество должно быть положительным!")
                    except ValueError:
                        print("❌ Ошибка: введите целое число!")
                else:
                    print(f"❌ Неверный индекс: {idx}")
            
            # Показываем текущий выбор
            if selected_items:
                print(f"\n📋 Текущий выбор: {', '.join([f'{item['name']}:{item['amount']}' for item in selected_items])}")
            
        except ValueError:
            print("❌ Ошибка: введите числа через пробел!")
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
    
    return selected_items

def add_focus(mother_name):
    name = input('Введите название фокуса: ')
    
    # Проверка на уникальность имени
    con = connect('focuses.db')
    cursor = con.cursor()
    cursor.execute("SELECT COUNT(*) FROM all_focuses WHERE name = ?", (name,))
    if cursor.fetchone()[0] > 0:
        print(f"❌ Фокус с именем '{name}' уже существует!")
        con.close()
        return
    
    # Добавляем в таблицу all_focuses
    cursor.execute("""
        INSERT INTO all_focuses (name, after)
        VALUES (?, ?)
    """, (name, mother_name))
    con.commit()
    
    # Запрашиваем остальные данные для таблицы focuses
    print(f"\n{'='*50}")
    print(f"=== Заполнение данных для фокуса '{name}' ===")
    print('='*50)
    
    # Описание фокуса (обязательное поле)
    desc = ''
    while not desc.strip():
        desc = input('Описание фокуса (обязательное поле): ')
        if not desc.strip():
            print("❌ Описание не может быть пустым!")
    
    emoji = input('Эмодзи: ') or None
    
    # Требуемые предметы
    req_items_list = get_selection_from_list(items, "предметов", "требуемых")
    req_items = format_requirements(req_items_list)
    
    # Требуемые фабрики
    req_factories_list = get_selection_from_list(factories, "фабрик", "требуемых")
    req_factories = format_requirements(req_factories_list)
    
    # Остальные поля
    print("\n=== Дополнительные поля ===")
    req_news = input('Требуемая новость (или Enter для пропуска): ') or None
    event = input('Событие (или Enter для пропуска): ') or None
    private_event = input('Приватное событие (или Enter для пропуска): ') or None
    
    # Фабрики, которые даёт фокус
    print("\n=== Фабрики, которые даёт фокус ===")
    factories_given_list = get_selection_from_list(factories, "фабрик", "получаемых")
    factories_given = format_requirements(factories_given_list)
    
    # Предметы, которые даёт фокус
    print("\n=== Предметы, которые даёт фокус ===")
    items_given_list = get_selection_from_list(items, "предметов", "получаемых")
    items_given = format_requirements(items_given_list)
    
    # Страны для войны
    print("\n=== Страны для объявления войны ===")
    war_list = []
    print_list_with_indexes(countries)
    
    while True:
        try:
            choice_input = input('Введите номер страны (или несколько через пробел, или "г" для завершения): ')
            
            if choice_input.lower() == 'г':
                break
            
            if not choice_input.strip():
                continue
            
            indexes = [int(idx.strip()) for idx in choice_input.split()]
            
            for idx in indexes:
                if 0 <= idx < len(countries):
                    country_name = countries[idx]
                    if country_name not in war_list:
                        war_list.append(country_name)
                        print(f"✅ Добавлена страна: {country_name}")
                    else:
                        print(f"⚠ Страна '{country_name}' уже добавлена!")
                else:
                    print(f"❌ Неверный индекс: {idx}")
            
            if war_list:
                print(f"📋 Текущий выбор: {', '.join(war_list)}")
                
        except ValueError:
            print("❌ Ошибка: введите числа через пробел!")
    
    war = '; '.join(war_list) if war_list else None
    
    # Вставляем данные в таблицу focuses
    cursor.execute("""
        INSERT INTO focuses (name, desc, emoji, req_items, req_factories, req_news, 
                           event, private_event, factories, items, war)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, desc, emoji, req_items, req_factories, req_news, event, 
          private_event, factories_given, items_given, war))
    
    con.commit()
    con.close()
    
    print(f"\n{'✅'*20}")
    print(f"✅ Фокус '{name}' успешно добавлен!")
    print(f"   Родительский фокус: {mother_name}")
    print(f"{'✅'*20}")

# Основной код
print("="*50)
print("ДОБАВЛЕНИЕ НОВОГО ФОКУСА")
print("="*50)

start_focus = input('Введите название начального фокуса для отображения цепочки: ')
all_focuses = get_all_focuses(start_focus)
items = fill_items()
factories = fill_factories()
countries = fill_countries()

# Выводим список фокусов для выбора
print("\n" + "="*50)
print("СПИСОК ФОКУСОВ ДЛЯ ВЫБОРА РОДИТЕЛЯ")
print("="*50)

if not all_focuses:
    print("❌ Не найдено фокусов для выбора!")
    exit()

focus_list = list(all_focuses.items())
for i, (name, children) in enumerate(focus_list):
    children_str = ', '.join(children) if children else '[КОНЕЦ ВЕТВИ]'
    print(f'[{i:2}] {name:30} → {children_str}')

while True:
    try:
        choice_input = input('\nВыберите номер фокуса-родителя: ')
        choice_idx = int(choice_input)
        
        if 0 <= choice_idx < len(focus_list):
            mother_focus = focus_list[choice_idx][0]
            print(f"\n✅ Выбран родительский фокус: {mother_focus}")
            add_focus(mother_focus)
        else:
            print(f"❌ Неверный номер! Допустимый диапазон: 0-{len(focus_list)-1}")
        # Основной код
        print("="*50)
        print("ДОБАВЛЕНИЕ НОВОГО ФОКУСА")
        print("="*50)

        all_focuses = get_all_focuses(start_focus)
        items = fill_items()
        factories = fill_factories()
        countries = fill_countries()
	
        # Выводим список фокусов для выбора
        print("\n" + "="*50)
        print("СПИСОК ФОКУСОВ ДЛЯ ВЫБОРА РОДИТЕЛЯ")
        print("="*50)
        focus_list = list(all_focuses.items())
        for i, (name, children) in enumerate(focus_list):
            children_str = ', '.join(children) if children else '[КОНЕЦ ВЕТВИ]'
            print(f'[{i:2}] {name:30} → {children_str}')

    except ValueError:
        print("❌ Ошибка: введите целое число!")