#from .library import (con, Row, DATABASE_PATH, 
#                      getinv, getfact, getbalance, 
#                      ROLE_PICKER_PATH, Interaction, bot, 
#                      guild, roles_id, Context,
#                      Member, TextChannel, Role,
#                      FOCUS_PATH, List, get_channel)
from .library import *



class Country:
    """Представляет страну в игре с её экономическими, социальными и ролевыми атрибутами.

    Класс инициализирует страну по имени, получает и управляет данными о её рынке,
    инвентаре, фабриках, балансе и привязанной роли на сервере Discord. Также отвечает
    за изменение статуса капитуляции, никнейма и открепление игрока.

    Attributes:
        name (str): Название страны.
        market (Market): Рынок страны, на котором происходят торговые операции.
        inventory (dict[str, Item]): Словарь предметов в инвентаре страны, где ключ — название предмета.
        factories (dict[str, Factory]): Словарь фабрик страны, где ключ — название фабрики.
        balance (int): Денежный баланс страны.
        busy (discord.Member | None): Участник Discord, привязанный к стране. None, если не привязан.
        surrend (bool): Флаг капитуляции страны. True, если страна капитулировала.
        sea (discord.Role | None): Роль морского флота страны на сервере Discord. Может быть None.
        assembly (discord.Role | None): Роль вхождения страну в ассамблею Лиги Наций. Может быть None.
        nickname (str): Отображаемое имя страны (никнейм участника).
    """

    def __init__(self, name: str = 'Италия'):
        """Инициализирует объект страны.

        Если имя передано в формате упоминания участника Discord (например, '<@123456789>'),
        то на основе этого упоминания извлекается реальное имя страны из базы данных.
        Затем загружаются все атрибуты страны: рынок, инвентарь, фабрики, баланс и роли.

        Args:
            name (str): Название страны или упоминание участника Discord. По умолчанию — 'Италия'.
        """
        if name.startswith('<@') and name.endswith('>'):
            connect = con(ROLE_PICKER_PATH)
            cursor = connect.cursor()
            
            cursor.execute(f"""
                            SELECT name
                            FROM roles
                            WHERE is_busy = {name}
            """)
            result = cursor.fetchone()
            if result:
                name = result[0]
            else:
                return
            connect.close() 
        
        self.name = name
        self.market = Market(name)
        self.inventory = getinv(name)
        self.factories = getfact(name)
        self.balance = getbalance(name)

        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        
        cursor.execute(f"""
                        SELECT is_busy, surrend, sea, assembly, nickname
                        FROM roles
                        WHERE name = '{name}'
                        """)
        fetch = cursor.fetchone()
        connect.close()
        
        self.busy = guild.get_member(int(fetch[0][2:-1])) if fetch and fetch[0] else None
        self.surrend = bool(fetch[1]) if fetch else False
        self.sea = guild.get_role(int(fetch[2])) if fetch and fetch[2] else None
        self.assembly = guild.get_role(int(fetch[3])) if fetch and fetch[3] else None
        self.nickname = fetch[4] if fetch and fetch[4] is not None else ""
        
        # Добавить в документацию
        connect = con(FOCUS_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT doing, completed
                        FROM countries
                        WHERE name = '{name}'
                        """)
        fetch = cursor.fetchone()
        cursor.close()

        if not fetch:
            return None
        
        self.doing_focus = Focus(fetch[0]) # добавить в документацию
        self.completed_focus = Focus(fetch[1]) # добавить в документацию
    
    def __str__(self):
        return self.name

    async def change_surrend(self, interaction: Interaction | None = None):
        """Переключает статус капитуляции страны.

        Если страна уже капитулировала, статус сбрасывается и игрок открепляется.
        В противном случае устанавливается статус капитуляции.

        Args:
            interaction (Interaction | None): Объект взаимодействия Discord. Если передан,
                имя страны берётся из значения выбора в интерактивном меню.
        """
        name = interaction.data['values'][0] if interaction else self.name
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()
        
        if self.surrend:
            cursor.execute(f"""
                            UPDATE roles
                            SET surrend = NULL
                            WHERE name = '{name}'
            """)
            self.surrend = False
            await self.unreg(interaction) 
        else:
            cursor.execute(f"""
                            UPDATE roles
                            SET surrend = '1'
                            WHERE name = '{self.name}'
            """)
            self.surrend = True
            
        connect.commit()
        connect.close()

    async def change_nickname(self, new_nickname: str):
        """Изменяет отображаемое имя (никнейм) страны в базе данных и у участника Discord.

        Если у страны привязан участник, пытается изменить его никнейм на сервере.

        Args:
            new_nickname (str): Новый никнейм для страны.
        """
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                       UPDATE roles
                       SET nickname = '{new_nickname}'
                       WHERE name = '{self.name}'
                       """)
        connect.commit()
        connect.close()
        
        if self.busy:
            try:
                await self.busy.edit(nick=new_nickname)
            except Exception:
                pass  # Игнорируем ошибки изменения никнейма

    async def unreg(self, interaction: Interaction | Context | None = None):
        """Открепляет участника Discord от страны и сбрасывает его роли.

        Удаляет все игровые роли у участника, добавляет роль "нерегистрированного",
        сбрасывает никнейм и обновляет базу данных.

        Args:
            interaction (Interaction | Context | None): Объект взаимодействия или контекста.
                Может использоваться для обратной связи, но не используется напрямую.
        """
        if not self.busy:
            return None
        
        user = self.busy
        for role_id in roles_id.values():
            try:
                role = guild.get_role(role_id) 
                if role:
                    await user.remove_roles(role) 
            except Exception:
                continue

        try:
            unreg_role = guild.get_role(1344519330091503628)
            if unreg_role:
                await user.add_roles(unreg_role)  
        except Exception:
            pass

        try:
            await user.edit(nick='') 
        except Exception:
            pass
        
        connect = con(ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                        UPDATE roles
                        SET is_busy = NULL
                        WHERE is_busy = '{self.busy.id}'
                        """)
        connect.commit()
        connect.close()
        self.busy = None

                

class Item:
    """Представляет игровой предмет с его свойствами и количеством в инвентаре страны.

    Класс используется для работы с предметами: их количеством, стоимостью, типом (наземный, воздушный, морской)
    и возможностью покупки. Данные о предмете загружаются из базы данных, а количество может быть привязано
    к конкретной стране.

    Attributes:
        name (str): Название предмета.
        quantity (int): Количество предмета в инвентаре страны.
        price (int): Стоимость предмета на рынке.
        purchasable (bool): Можно ли покупать предмет на рынке.
        is_ship (bool): Является ли предмет морским (кораблём).
        is_ground (bool): Является ли предмет наземным (техникой).
        is_air (bool): Является ли предмет воздушным (самолётом).
    """

    def __init__(self, name: str, quantity: int | None = None, price: int = 0, country: str | Country | None = None):
        """Инициализирует объект предмета.

        Если количество не указано, оно загружается из инвентаря страны. Также из базы данных
        загружаются атрибуты предмета: возможность торговли и принадлежность к типу техники.

        Args:
            name (str): Название предмета (должно соответствовать записи в базе данных).
            quantity (int | None): Количество предмета. Если None — загружается из инвентаря страны.
            price (int): Стоимость предмета. По умолчанию — 0.
            country (str | Country | None): Страна, чей инвентарь используется для определения количества.
                Может быть строкой с названием или объектом Country.
        """
        self.name = name
        self.quantity = quantity if quantity is not None else (getinv(country, name).quantity if country else 0)
        self.price = price

        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT *
                        FROM items
                        WHERE name = '{name}'
                        """)
        items_info = dict(cursor.fetchone())
        connect.close()

        self.purchasable = int(items_info['tradable']) == 1
        self.is_ship = int(items_info['ship']) == 1
        self.is_ground = int(items_info['ground']) == 1
        self.is_air = int(items_info['air']) == 1

    def edit_quantity(self, quantity: int, country: str | Country) -> None:
        """Изменяет количество предмета в инвентаре указанной страны.

        Обновляет значение в базе данных и в локальном объекте.

        Args:
            quantity (int): Новое количество предмета.
            country (str | Country): Страна, для которой обновляется количество.
                Может быть передана как объект Country или строка с названием.

        Returns:
            None
        """
        country_name = country.name if isinstance(country, Country) else country
        self.quantity = quantity
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        UPDATE country_inventories
                        SET `{self.name}` = {quantity}
                        WHERE `name` = '{country_name}'
        """)
        connect.commit()
        connect.close()


class Market:
    """Представляет рынок конкретной страны для торговли предметами.

    Класс управляет коллекцией выставленных на продажу предметов, их количеством и ценой.
    При инициализации загружает данные из базы данных или создаёт новую запись для страны.
    Поддерживает операции добавления, изменения, удаления и получения предметов.

    Attributes:
        name (str): Название страны, чей рынок представлен.
        inventory (dict): Словарь предметов на рынке, где ключ — название предмета, значение — объект Item.
    """

    def __init__(self, country: str | Country):
        """Инициализирует объект рынка для указанной страны.

        Если запись о рынке страны отсутствует в базе данных, она создаётся.
        Загружает все выставленные предметы и их параметры (количество и цену).

        Args:
            country (str | Country): Страна, для которой создаётся или загружается рынок.
                Может быть передана как строка с названием или объект Country.
        """
        country_name = country.name if isinstance(country, Country) else country
        self.name = country_name
        self.inventory = {}

        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        try:
            cursor.execute(f"""
                SELECT *
                FROM market
                WHERE name = '{country_name}'
            """)
        except:
            # Если таблица или запись не существует, создаём запись
            cursor.execute(f"""
                INSERT INTO market (name)
                VALUES ('{country_name}')
            """)
            connect.commit()

            cursor.execute(f"""
                SELECT *
                FROM market
                WHERE name = '{country_name}'
            """)
        
        result = dict(cursor.fetchone())
        connect.close()

        # Парсим поля: каждое поле (кроме 'name') содержит строку вида "количество цена"
        for name, value in result.items():
            if name != 'name' and value:
                parts = value.split()
                quantity = int(parts[0]) if len(parts) > 0 else 0
                price = int(parts[1]) if len(parts) > 1 else 0
                self.inventory[name] = Item(name, quantity, price)

    def get_inv(self, quest: bool = False) -> dict:
        """Возвращает инвентарь рынка.

        При необходимости включает только предметы с ненулевым количеством.

        Args:
            quest (bool): Если True, включаются все предметы, включая те, что с нулевым количеством.
                По умолчанию False — возвращаются только предметы с количеством больше нуля.

        Returns:
            dict: Словарь предметов на рынке.
        """
        result = {}
        for name, item in self.inventory.items():
            if item.quantity > 0 or quest:
                result[name] = item
        return result

    def add_item(self, item: Item) -> None:
        """Добавляет новый предмет на рынок.

        Создаёт новую колонку в записи рынка страны и добавляет предмет в локальный инвентарь.

        Args:
            item (Item): Объект предмета, который нужно добавить на рынок.

        Returns:
            None
        """
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
            INSERT INTO market (name, `{item.name}`)
            VALUES ('{self.name}', '{item.quantity} {item.price}')
        """)
        connect.commit()
        connect.close()
        self.inventory[item.name] = item

    def edit_item(self, item: Item) -> None:
        """Обновляет информацию о предмете на рынке.

        Если предмета ещё нет в инвентаре рынка, он добавляется.
        В противном случае обновляются его количество и цена в базе данных и локально.

        Args:
            item (Item): Объект предмета с новыми значениями количества и цены.

        Returns:
            None
        """
        if item.name not in self.inventory:
            self.add_item(item)
            return None

        self.inventory[item.name] = item
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
            UPDATE market
            SET `{item.name}` = '{item.quantity} {item.price}'
            WHERE name = '{self.name}'
        """)
        connect.commit()
        connect.close()

    def remove_item(self, item: Item | str) -> None:
        """Удаляет предмет с рынка, устанавливая его количество и цену в "0 0".

        Предмет остаётся в базе данных, но становится недоступным для покупки.

        Args:
            item (Item | str): Объект предмета или его название в виде строки.

        Returns:
            None
        """
        item_name = item.name if isinstance(item, Item) else item
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
            UPDATE market
            SET `{item_name}` = '0 0'
            WHERE name = '{self.name}'
        """)
        connect.commit()
        connect.close()


class Factory:
    """Представляет тип фабрики в игре с её характеристиками и количеством в стране.

    Класс используется для работы с производственными объектами: их производительностью,
    стоимостью, описанием и количеством в определённой стране. Данные о типе фабрики
    загружаются из базы данных, количество может быть привязано к стране.

    Attributes:
        name (str): Название фабрики.
        quantity (int): Количество фабрик данного типа в стране.
        country (Country | None): Объект страны, которой принадлежат фабрики. Может быть None.
        produces (str): Ключ производимого предмета (например, название товара).
        count (float): Количество единиц продукции, производимых одной фабрикой за период.
        desc (str): Описание фабрики.
        cost (int): Стоимость постройки одной единицы фабрики.
    """

    def __init__(self, factory_name: str, quantity: int | None = None, country: str | Country | None = None):
        """Инициализирует объект фабрики.

        Если количество не указано, оно загружается из данных страны. Также из базы данных
        загружаются атрибуты фабрики: что производит, производительность, стоимость и описание.

        Args:
            factory_name (str): Название фабрики (должно соответствовать записи в таблице 'factories').
            quantity (int | None): Количество фабрик. Если None — загружается из данных страны.
            country (str | Country | None): Страна, в которой находятся фабрики. Может быть строкой или объектом Country.
        """
        self.name = factory_name
        self.quantity = quantity if quantity is not None else (getfact(country, factory_name).quantity if country else 0)
        self.country = Country(country) if country else None

        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT *
                        FROM factories
                        WHERE name = '{factory_name}'
        """)
        fetch = cursor.fetchone()
        connect.close()

        if fetch is None:
            raise ValueError(f"Фабрика с именем '{factory_name}' не найдена в базе данных.")

        self.produces = fetch['produces_key']
        self.count = float(fetch['count'])
        self.desc = fetch['desc']
        self.cost = int(fetch['cost'])

    def edit_quantity(self, quantity: int, country: str | Country) -> None:
        """Изменяет количество фабрик данного типа в указанной стране.

        Обновляет значение в базе данных и в локальном объекте.

        Args:
            quantity (int): Новое количество фабрик.
            country (str | Country): Страна, для которой обновляется количество.
                Может быть передана как объект Country или строка с названием.

        Returns:
            None
        """
        country_name = country.name if isinstance(country, Country) else country
        self.quantity = quantity
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        UPDATE countries_factory
                        SET `{self.name}` = {quantity}
                        WHERE `name` = '{country_name}'
        """)
        connect.commit()
        connect.close()



class Focus:
    def __init__(self, name: str, owner: Country | None = None):
        connect = con(FOCUS_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute(f"""
                       SELECT *
                       FROM focuses
                       WHERE name = '{name}'
                       """)
        fetch = cursor.fetchone()
        connect.close()

        self.owner = owner
        self.name: str = fetch['name']
        self.desc: str = fetch['desc']
        self._req: str | None = fetch['req']
        self.event: str | None = fetch['event']
        self._factories: List[Factory] | None = fetch['factories']
        self._items: List[Item] | None = fetch['items']
        self._war: List[Country] | None = fetch['war']

        self._factories = self._factories.split('; ') if self._factories else []
        for i in range(len(self._factories)):
            self._factories[i] = Factory(self._factories[i].split(':')[0], int(self._factories[i].split(':')[1]))
        
        self._items = self._items.split('; ') if self._items else []
        for i in range(len(self._items)):
            self._items[i] = Item(self._items[i].split(':')[0], int(self._items[i].split(':')[1]))
        
        self._war = [Country(i) for i in self._war.split('; ')]

    async def send_event(self):
        """Отправляет событие в текстовый канал, заменяя переменные {страна} на упоминания участников, если они заняты."""
        if not self.event:
            return

        text = self.event

        import re
        # Находим все вхождения {...}
        variables = re.findall(r"\{([^}]+)\}", text)
 
        for var in variables:
            # Предполагаем, что var — это название страны
            try:
                country = Country(var.strip())
                # Проверяем, занята ли страна
                if country.busy:
                    mention = f"<@{country.busy.id}>"
                    text = text.replace(f"{{{var}}}", mention)
                else:
                    text = text.replace(f"{{{var}}}", "")
            except:
                # Если страна не найдена в базе — просто удаляем переменную
                text = text.replace(f"{{{var}}}", "")

        # -- это нейронка написала, как страшно -- 
        # Убираем лишние пробелы и знаки препинания (например, "на  , атаковал" → "на, атаковал" → "на атаковал")
        # Удаляем множественные пробелы и очищаем пробелы вокруг знаков препинания
        text = re.sub(r"\s+", " ", text)  # Заменяем множественные пробелы
        text = re.sub(r"\s*([,.!?;:])\s*", r"\1 ", text)  # Очищаем пробелы вокруг знаков препинания
        text = re.sub(r"\s+", " ", text).strip()  # Ещё раз убираем лишние пробелы
        text = re.sub(r"^\W+|\W+$", "", text)  # Убираем знаки препинания в начале/конце
        text = text.strip()

        if not text:
            return

        await get_channel('event').send(text)
