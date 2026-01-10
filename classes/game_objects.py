#from .library import (con, Row, DATABASE_PATH, 
#                      getinv, getfact, getbalance, 
#                      ROLE_PICKER_PATH, Interaction, bot, 
#                      guild, roles_id, Context,
#                      Member, TextChannel, Role,
#                      FOCUS_PATH, List, get_channel)
from .library import Row, Interaction, Context, List, Attachment
from .library import connect as con
import dependencies as deps



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
        from .library import getinv, getfact, getbalance
        self.busy = None
        self.is_country = True
        if name.startswith('<@') and name.endswith('>'):
            conn = con(deps.DATABASE_ROLE_PICKER_PATH)
            cursor = conn.cursor()
            
            cursor.execute(f"""
                            SELECT name
                            FROM roles
                            WHERE is_busy = '{name}'
            """)
            result = cursor.fetchone()
            if result:
                name = result[0]
            else:
                self.is_country = False
                return
            conn.close() 
        
        self.name = name
        self.market = Market(name)
        self.inventory = getinv(name)
        self.factories = getfact(name)
        self.balance = getbalance(name)

        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()
        
        cursor.execute(f"""
                        SELECT is_busy, surrender, sea, assembly, nickname
                        FROM roles
                        WHERE name = '{name}'
                        """)
        fetch = cursor.fetchone()
        connect.close()
        
        self.busy = deps.guild.get_member(int(fetch[0][2:-1])) if fetch and fetch[0] else None
        self.surrend = bool(fetch[1]) if fetch else False
        self.sea = deps.guild.get_role(int(fetch[2])) if fetch and fetch[2] else None
        self.assembly = deps.guild.get_role(int(fetch[3])) if fetch and fetch[3] else None
        self.nickname = fetch[4] if fetch and fetch[4] is not None else ""
        
        # Добавить в документацию
        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT doing, current
                        FROM countries
                        WHERE name = '{name}'
                        """)
        fetch = cursor.fetchone()
        cursor.close()

        if not fetch:
            return None
        
        self.doing_focus = Focus(fetch[0], self) if fetch[0] else None # добавить в документацию
        self.current_focus = Focus(fetch[1], self) # добавить в документацию
    
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
        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
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
        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
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
            except:
                pass  # Игнорируем ошибки изменения никнейма -> translate: Ignore

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
        for role_id in deps.RP_ROLES.values():
            try:
                role = deps.guild.get_role(role_id) 
                if role:
                    await user.remove_roles(role) 
            except Exception:
                continue

        try:
            unreg_role = deps.guild.get_role(1344519330091503628)
            if unreg_role:
                await user.add_roles(unreg_role)  
        except Exception:
            pass

        try:
            await user.edit(nick='') 
        except Exception:
            pass
        
        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                        UPDATE roles
                        SET is_busy = NULL
                        WHERE is_busy = '{self.busy.id}'
                        """)
        connect.commit()
        connect.close()
        self.busy = None

    async def send_news(self, news: str, attachments: List[Attachment]):
        """Отправляет новостное сообщение в канал новостей стран.

        Args:
            news (str): Текст новости для отправки.
        """
        files = [await file.to_file() for file in attachments]
        channel = deps.rp_channels.get_news()

        # Попытка загрузить аватар из БД
        avatar_bytes = None
        try:
            conn = con(deps.DATABASE_COUNTRIES_AI_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT avatar FROM avatars WHERE name = ?", (self.name,))
            row = cursor.fetchone()
            conn.close()
            avatar_bytes = row[0] if row and row[0] else None
        except Exception:
            avatar_bytes = None

        try:
            # Если нет аватара, попробуем использовать первый доступный вебхук
            if not avatar_bytes:
                webhooks = await channel.webhooks()
                if webhooks:
                    await webhooks[0].send(content=news, username=self.name)
                    return

            # Создаём временный вебхук (с аватаром, если он есть) и отправляем сообщение
            if avatar_bytes:
                webhook = await channel.create_webhook(name=self.name, avatar=avatar_bytes)
            else:
                webhook = await channel.create_webhook(name=self.name)

            await webhook.send(content=news, username=self.name)
        finally:
            # Удаляем временный вебхук, если он был создан
            try:
                if 'webhook' in locals():
                    await webhook.delete()
            except Exception:
                pass
                
    def give_available_focuses(self) -> list['Focus']:
        """Возвращает список доступных национальных фокусов для страны.

        Фокусы загружаются из базы данных и фильтруются по критериям доступности
        для текущей страны.

        Returns:
            List[Focus]: Список доступных фокусов.
        """
        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       SELECT name
                       FROM all_focuses
                       WHERE after = ?
                       """, (self.current_focus.name,))
        result = cursor.fetchall()
        connect.close()

        return [Focus(row[0]) for row in result]

    def set_focus(self, focus):
        focus: Focus | str = focus
        new_focus = focus.name if isinstance(focus, Focus) else focus
        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                          UPDATE countries
                          SET doing = '{new_focus}'
                          WHERE name = '{self.name}'
                        """)
        connect.commit()
        connect.close()
        self.doing_focus = focus if isinstance(focus, Focus) else Focus(focus, self)

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
        from .library import getinv
        self.name = name
        self.quantity = quantity if quantity is not None else (getinv(country, name).quantity if country else 0)
        self.price = price
        self.country = Country(country) if isinstance(country, str) else (country if isinstance(country, Country) else None)

        connect = con(deps.DATABASE_COUNTRIES_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT *
                        FROM items
                        WHERE name = '{name}'
                        """)
        items_info = dict(cursor.fetchone())
        connect.close()

        if items_info is None:
            raise ValueError(f"Предмет с именем '{name}' не найдена в базе данных.")
        
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
        connect = con(deps.DATABASE_COUNTRIES_PATH)
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
        self.inventory: dict[str, Item] = {}

        connect = con(deps.DATABASE_COUNTRIES_PATH)
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
        
        fetch = cursor.fetchone()
        if not fetch:
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
            fetch = cursor.fetchone()
        
        result = dict(fetch)
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
        connect = con(deps.DATABASE_COUNTRIES_PATH)
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
        connect = con(deps.DATABASE_COUNTRIES_PATH)
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
        connect = con(deps.DATABASE_COUNTRIES_PATH)
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
        from .library import getfact
        self.name = factory_name
        self.quantity = quantity if quantity is not None else (getfact(country, factory_name).quantity if country else 0)
        self.country = Country(country) if isinstance(country, str) else (country if isinstance(country, Country) else None)

        connect = con(deps.DATABASE_COUNTRIES_PATH)
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
        connect = con(deps.DATABASE_COUNTRIES_PATH)
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
        connect = con(deps.DATABASE_FOCUS_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute(f"""
                       SELECT *
                       FROM focuses
                       WHERE name = '{name}'
                       """)
        fetch = cursor.fetchone()
        fetch = dict(fetch) if fetch else None
        connect.close()

        self.owner: Country | None = owner
        self.name: str = fetch['name']
        """Название фокуса"""

        self.description: str = fetch['desc']
        """Описание фокуса"""

        self.emoji: str | None = fetch['emoji']
        """Эмодзи фокуса"""


        self.req_items: List[Item] | None = fetch['req_items']
        """Требуемые предметы для выполнения фокуса"""

        self.req_factories: list[Factory] | None = fetch['req_factories']
        """Требуемые фабрики для выполнения фокуса"""

        self.req_news: bool = fetch['req_news'] is not None
        """Требуется ли новостное сообщение для выполнения фокуса"""

        self.event: str | None = fetch['event']
        """Событие, которое происходит при выполнении фокуса"""


        self.factories: List[Factory] | None = fetch['factories']
        """Фабрики, которые даёт фокус"""

        self.items: List[Item] | None = fetch['items']
        """Предметы, которые даёт фокус"""

        self.war: List[Country] | None = fetch['war']
        """Страны, с которыми объявляется война при выполнении фокуса"""
        
        self.items = self.items.split('; ') if self.items else []
        for i in range(len(self.items)):
            self.items[i] = Item(self.items[i].split(':')[0], int(self.items[i].split(':')[1]))
        
        self.req_items = self.req_items.split('; ') if self.req_items else []
        for i in range(len(self.req_items)):
            self.req_items[i] = Item(self.req_items[i].split(':')[0], int(self.req_items[i].split(':')[1]))

        self.factories = self.factories.split('; ') if self.factories else []
        for i in range(len(self.factories)):
            self.factories[i] = Factory(self.factories[i].split(':')[0], int(self.factories[i].split(':')[1]))
        
        self.req_factories = self.req_factories.split('; ') if self.req_factories else []
        for i in range(len(self.req_factories)):
            self.req_factories[i] = Factory(self.req_factories[i].split(':')[0], int(self.req_factories[i].split(':')[1]))
        
        self.war = [Country(i) for i in self.war.split('; ')] if self.war else []

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

        # -- это нейронка написала, мне страшно -- 
        # Убираем лишние пробелы и знаки препинания (например, "на  , атаковал" → "на, атаковал" → "на атаковал")
        # Удаляем множественные пробелы и очищаем пробелы вокруг знаков препинания
        text = re.sub(r"\s+", " ", text)  # Заменяем множественные пробелы
        text = re.sub(r"\s*([,.!?;:])\s*", r"\1 ", text)  # Очищаем пробелы вокруг знаков препинания
        text = re.sub(r"\s+", " ", text).strip()  # Ещё раз убираем лишние пробелы
        text = re.sub(r"^\W+|\W+$", "", text)  # Убираем знаки препинания в начале/конце
        text = text.strip()

        if not text:
            return

        deps.rp_channels.get_event().send(text)
    
    async def declare_war(self):
        if len(self.war) == 0:
            return
        countries = [i.name for i in self.war]
        title = f'{self.owner} Объявляет войну ' + ('Государству ' + countries[0] if len(countries) == 1 else 'Государствам ' + ', '.join(countries))
        content = 'По какой-то невиданной мне причине куратор так и не нашелся. В таком случае нам всем придется подождать!\n' + '||' + self.owner.busy.mention + ', ' + ', '.join([i.busy.mention for i in self.war if i.busy]) + '||'
        await deps.rp_channels.get_war().create_thread(name=title, content=content)
    
    def send_factories(self):
        for factory in self.factories:
            factory.edit_quantity(self.owner.factories[factory.name].quantity + factory.quantity, self.owner)
    def send_items(self):
        for item in self.items:
            item.edit_quantity(self.owner.inventory[item.name].quantity + item.quantity, self.owner)
        
    def requirements_complete(self) -> bool:
        for item in self.req_items:
            if self.owner.inventory[item.name].quantity < item.quantity:
                return False
        for factory in self.req_factories:
            if self.owner.factories[factory.name].quantity < factory.quantity:
                return False
        return True
    
    def mark_as_completed(self):
        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()
        
        cursor.execute("""
                        UPDATE countries
                        SET completed = ?
                        """, (self.name,))
        connect.commit()
        connect.close()
    
    async def complete_focus(self):
        self.send_factories()
        self.send_items()
        await self.send_event()
        await self.declare_war()

