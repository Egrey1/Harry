"""Здесь хранятся глобальные переменные и объекты, используемые в боте."""

from discord import Guild, Intents, TextChannel, ForumChannel, Role, Interaction, Attachment, Member
from discord.ext.commands import Bot, Context
from discord.ui import Button, Select
from typing import List, Callable, Awaitable

bot: Bot = Bot('!', intents=Intents.all())
DATABASE_ROLE_PICKER_PATH: str
DATABASE_COUNTRIES_PATH: str
DATABASE_FOCUS_PATH: str
DATABASE_CONFIG_PATH: str
DATABASE_COUNTRY_AI_PATH: str

CURRENCY: str
RP_ROLES: dict
PERSONAL: dict[str, Role]

CHANNEL_FOR_UPDATE_ID: int
"""Канал, который будет обновляться каждую единицу времени"""

guild_id: int
"""Detrimentum"""
guild: Guild
"""Detrimentum"""

game_state: dict
PAGE_SIZE: int = 25
register_cooldown: int = 1
diminishing_returns: int = 0.95

SPEED: int = 1 # В часах

TOKEN: str
TOKEN1: str
TOKEN2: str
PREFIX: str
intents: Intents

audit: TextChannel

class Country:
    """Представляет страну в игре с её экономическими, социальными и ролевыми атрибутами.
    
    Класс управляет всеми аспектами жизни игровой страны: экономикой, фабриками,
    инвентарём, ролями на Discord сервере и национальными фокусами. Может быть
    инициализирован либо по названию страны, либо по упоминанию игрока Discord.
    
    Attributes:
        name (str): Название страны. Загружается из БД roles таблицы.
        id (str): Уникальный идентификатор страны из БД roles таблицы.
        market (Market): Объект рынка страны для торговых операций.
        inventory (dict[str, Item]): Словарь предметов инвентаря {название: Item}.
        factories (dict[str, Factory]): Словарь фабрик страны {название: Factory}.
        balance (int): Текущий денежный баланс страны.
        busy (discord.Member | None): Discord участник, привязанный к стране (None если не привязан).
        is_country (bool): Флаг валидности страны (True если страна существует и валидна).
        surrend (bool): Флаг капитуляции (True если страна капитулировала).
        sea (discord.Role | None): Discord роль морского флота страны (None если не имеется).
        assembly (discord.Role | None): Discord роль членства в Лиге Наций (None если не имеется).
        nickname (str): Отображаемое имя игрока в контексте страны.
        doing_focus (Focus | None): Текущий выполняемый национальный фокус (None если нет).
        current_focus (Focus | None): Последний завершённый национальный фокус (None если нет).
        building_slots (int): Количество строительных ячеек для размещения фабрик.
    """

    def __init__(self, name: str = 'Италия') -> None:
        """Инициализирует объект страны по названию или упоминанию Discord.
        
        Загружает все данные страны из базы данных:
        - Из roles таблицы: статус занятости, капитуляции, роли и никнейм
        - Из countries таблицы: текущие фокусы
        - Из country_info таблицы: количество строительных ячеек
        
        Если передано упоминание в формате '<@123456789>', извлекается имя страны
        из поля is_busy в БД. Если страна не найдена, устанавливается is_country=False.
        
        Args:
            name (str): Название страны или упоминание Discord участника (формат '<@ID>').
                По умолчанию 'Италия'.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_ROLE_PICKER_PATH: таблица roles (поля: name, is_busy, surrender, 
              sea, assembly, nickname)
            - DATABASE_FOCUS_PATH: таблица countries (поля: name, doing, current)
            - DATABASE_COUNTRY_AI_PATH: таблица country_info (поле: building_slots)
            
            Используемые функции:
            - getinv(name): получение инвентаря страны
            - getfact(name): получение фабрик страны
            - getbalance(name): получение баланса страны
        """
        self.name: str
        """Название страны. Загружается из БД roles таблицы."""
        self.id: str
        """Уникальный идентификатор страны из БД roles таблицы."""
        self.market: Market
        """Объект рынка страны для торговых операций."""
        self.inventory: dict[str, Item]
        """Словарь предметов инвентаря {название: Item}."""
        self.factories: dict[str, Factory]
        """Словарь фабрик страны {название: Factory}."""
        self.balance: int
        """Текущий денежный баланс страны."""
        self.busy: 'Member | None'
        """Discord участник, привязанный к стране (None если не привязан)."""
        self.is_country: bool
        """Флаг валидности страны (True если страна существует и валидна)."""
        self.surrend: bool
        """Флаг капитуляции (True если страна капитулировала)."""
        self.sea: 'Role | None'
        """Discord роль морского флота страны (None если не имеется)."""
        self.assembly: 'Role | None'
        """Discord роль членства в Лиге Наций (None если не имеется)."""
        self.nickname: str
        """Отображаемое имя игрока в контексте страны."""
        self.doing_focus: 'Focus | None'
        """Текущий выполняемый национальный фокус (None если нет)."""
        self.current_focus: 'Focus | None'
        """Последний завершённый национальный фокус (None если нет)."""
        self.building_slots: int
        """Количество строительных ячеек для размещения фабрик."""
        ...

    def _load_building_slots(self) -> int:
        """Загружает лимит строительных ячеек из базы данных.
        
        Получает максимальное количество фабрик, которые может иметь страна.
        В случае отсутствия записи в БД или ошибки логирует проблему и отправляет
        сообщение об ошибке в канал audit, возвращая 0.
        
        Returns:
            int: Количество доступных строительных ячеек (слотов). 0 если ошибка или 
                запись не найдена.
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRY_AI_PATH: таблица country_info (поле: building_slots)
                WHERE name = self.name
            
            Побочные эффекты:
            - Логирует ошибки при их возникновении
            - Отправляет сообщения об ошибках в канал deps.audit
        """
        ...

    def get_used_building_slots(self) -> int:
        """Вычисляет количество строительных ячеек, занятых фабриками страны.
        
        Суммирует количество всех фабрик страны, исключая специальную фабрику
        'Коммерческая зона' (временное исключение).
        
        Returns:
            int: Количество используемых строительных ячеек.
        
        Note:
            Итерирует по self.factories (dict[str, Factory]) и суммирует
            Factory.quantity, исключая factory.name == 'Коммерческая зона'.
            
            TODO: Исправить логику исключения Коммерческой зоны.
        """
        ...

    def get_available_building_slots(self) -> int:
        """Вычисляет количество свободных строительных ячеек для новых фабрик.
        
        Returns:
            int: Количество доступных (свободных) строительных ячеек.
                Равно: building_slots - get_used_building_slots()
        """
        ...

    def increase_building_slots(self, amount: int) -> bool:
        """Увеличивает лимит строительных ячеек и сохраняет в БД.
        
        Добавляет указанное количество ячеек к текущему лимиту. Гарантирует,
        что новый лимит не будет меньше текущего количества использованных ячеек
        (всегда valid состояние). Обновляет БД и локальный объект.
        
        Args:
            amount (int): Количество ячеек для добавления (обычно результат фокуса).
        
        Returns:
            bool: True если успешно обновлено, False если произошла ошибка.
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRY_AI_PATH: таблица country_info
                UPDATE building_slots WHERE name = self.name
            
            Логика:
            - Если новый лимит < используемых ячеек, устанавливает лимит = используемые ячейки
            - Логирует предупреждения и ошибки
            - Отправляет ошибки в канал deps.audit
        """
        ...

    def __str__(self) -> str:
        """Строковое представление страны.
        
        Returns:
            str: Название страны (self.name)
        """
        ...

    async def change_surrend(self, interaction: 'Interaction | None' = None) -> None:
        """Переключает статус капитуляции страны и управляет ролями игрока.
        
        Если страна уже капитулировала:
        - Убирает статус капитуляции из БД
        - Вызывает unreg() для открепления игрока
        
        Если страна не капитулировала:
        - Устанавливает статус капитуляции в БД
        
        Args:
            interaction (Interaction | None): Discord взаимодействие. Если передано,
                имя страны берётся из interaction.data['values'][0]. Если None,
                используется self.name.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_ROLE_PICKER_PATH: таблица roles
                UPDATE surrender WHERE name = {name}
                
            Побочные эффекты:
            - При капитуляции вызывает self.unreg(interaction)
            - Изменяет self.surrend флаг
        """
        ...

    async def change_nickname(self, new_nickname: str) -> None:
        """Изменяет никнейм страны в БД и на Discord сервере.
        
        Обновляет никнейм в таблице БД и пытается установить никнейм привязанного
        Discord участника на сервере. Ошибки при изменении никнейма на сервере
        игнорируются (может быть недостаточно прав).
        
        Args:
            new_nickname (str): Новый никнейм для страны.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_ROLE_PICKER_PATH: таблица roles
                UPDATE nickname WHERE name = self.name
            
            Побочные эффекты:
            - Пытается вызвать self.busy.edit(nick=new_nickname) если busy не None
            - Игнорирует ошибки Discord API
        """
        ...

    async def unreg(self, interaction: 'Interaction | Context | None' = None) -> None:
        """Открепляет Discord участника от страны и сбрасывает его роли.
        
        Удаляет все игровые роли (из RP_ROLES), добавляет роль "нерегистрированного",
        сбрасывает никнейм участника и обновляет БД (устанавливает is_busy = NULL).
        
        Args:
            interaction (Interaction | Context | None): Контекст взаимодействия.
                На текущий момент не используется напрямую, может использоваться
                для обратной связи.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_ROLE_PICKER_PATH: таблица roles
                UPDATE is_busy = NULL WHERE is_busy = self.busy.mention
            
            Discord роли:
            - Удаляет: все роли из deps.RP_ROLES.values()
            - Добавляет: роль с ID 1344519330091503628 (нерегистрированные)
            
            Побочные эффекты:
            - Вызывает await user.remove_roles() и await user.add_roles()
            - Вызывает await user.edit(nick='')
            - Устанавливает self.busy = None
            - Игнорирует все Discord API ошибки
        """
        ...

    async def send_news(self, news: str, attachments: 'List[Attachment]', view) -> None:
        """Отправляет новостное сообщение в канал новостей стран.
        
        Создаёт временный Discord вебхук с аватаром страны (если имеется в БД)
        и отправляет сообщение новости с возможными вложениями. После отправки
        вебхук удаляется.
        
        Args:
            news (str): Текст новости для отправки.
            attachments (List[Attachment]): Список attachments для отправки с новостью.
            view: Discord View объект с кнопками для взаимодействия с новостью.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRY_AI_PATH: таблица avatars
                SELECT avatar WHERE name = self.name
            
            Discord каналы:
            - Отправляет в канал с ID: 1429571616982958222 (канал новостей)
            
            Логика:
            - Если нет аватара и есть вебхуки: использует существующий вебхук
            - Если нет аватара: создаёт новый вебхук без аватара
            - Если есть аватар: создаёт вебхук с аватаром из БД
            - В finally блоке удаляет созданный вебхук (если был создан)
            
            Побочные эффекты:
            - Создаёт и удаляет временный вебхук
            - Отправляет сообщение на Discord сервер
        """
        ...

    def give_available_focuses(self) -> list['Focus']:
        """Получает список доступных национальных фокусов для страны.
        
        Возвращает все фокусы, которые следуют за текущим завершённым фокусом.
        Если текущего фокуса нет, возвращает пустой список.
        
        Returns:
            list[Focus]: Список доступных фокусов. Пустой список если нет 
                current_focus или нет доступных фокусов.
        
        Note:
            Используемые БД:
            - DATABASE_FOCUS_PATH: таблица all_focuses
                SELECT name WHERE after = self.current_focus.name
            
            Логика:
            - Если self.current_focus is None: возвращает []
            - Иначе запрашивает все фокусы с after = current_focus.name
            - Возвращает список объектов Focus
        """
        ...

    def set_focus(self, focus: 'Focus | str') -> None:
        """Устанавливает выполняемый национальный фокус и сохраняет в БД.
        
        Обновляет поле 'doing' в БД и локальный объект self.doing_focus.
        Принимает либо объект Focus, либо строку с названием фокуса.
        
        Args:
            focus (Focus | str): Объект Focus или строка с названием фокуса для установки.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_FOCUS_PATH: таблица countries
                UPDATE doing = {new_focus} WHERE name = self.name
            
            Логика:
            - Если focus это Focus объект: использует focus.name
            - Если focus это str: использует как есть
            - Обновляет БД и self.doing_focus
        """
        ...

    def get_expenses(self) -> int:
        """Вычисляет общие расходы страны на поддержание фабрик.
        
        Суммирует maintenance всех фабрик, умноженных на их количество.
        
        Returns:
            int: Общая сумма расходов на поддержание фабрик.
        """
        ...
    
    def get_earnings(self) -> int:
        """Вычисляет общие доходы страны (в деньгах) от производства фабрик.
        
        Суммирует count всех фабрик, умноженных на их количество.
        
        Returns:
            int: Общая сумма доходов от производства фабрик.
        """
        ...


class Item:
    """Представляет игровой предмет с его свойствами и количеством в инвентаре страны.
    
    Класс используется для работы с предметами: их количеством, стоимостью, типом
    (наземный, воздушный, морской) и возможностью покупки. Данные о предмете загружаются
    из базы данных, а количество может быть привязано к конкретной стране.
    
    Attributes:
        name (str): Название предмета.
        quantity (int): Количество предмета в инвентаре страны.
        price (int): Стоимость предмета на рынке.
        purchasable (bool): Можно ли покупать предмет на рынке (из поля tradable).
        is_ship (bool): Является ли предмет морским кораблём (флаг ship).
        is_ground (bool): Является ли предмет наземной техникой (флаг ground).
        is_air (bool): Является ли предмет воздушным (самолётом) (флаг air).
        country (Country | None): Объект страны, если был передан при инициализации.
        produced_by (List[Factory] | None): Фабрики, которые производят этот предмет (None если не привязан).
        id (str): Уникальный идентификатор предмета из БД items таблицы
    """

    def __init__(self, name: str, quantity: int | None = None, price: int = 0, 
                 country: 'str | Country | None' = None) -> None:
        """Инициализирует объект игрового предмета.
        
        Если количество не указано, оно загружается из инвентаря страны. Атрибуты
        предмета (торговаемость, тип техники) загружаются из базы данных.
        
        Args:
            name (str): Название предмета (должно соответствовать записи в БД).
            quantity (int | None): Количество предмета. Если None, загружается из 
                инвентаря страны.
            price (int): Стоимость предмета. По умолчанию 0.
            country (str | Country | None): Страна, чей инвентарь используется.
                Может быть строкой с названием или объектом Country.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRIES_PATH: таблица items
                SELECT tradable, ship, ground, air WHERE name = {name}
        """
        self.name: str
        """Название предмета."""
        self.quantity: int
        """Количество предмета в инвентаре страны."""
        self.price: int
        """Стоимость предмета на рынке."""
        self.purchasable: bool
        """Можно ли покупать предмет на рынке (из поля tradable)."""
        self.is_ship: bool
        """Является ли предмет морским кораблём (флаг ship)."""
        self.is_ground: bool
        """Является ли предмет наземной техникой (флаг ground)."""
        self.is_air: bool
        """Является ли предмет воздушным (самолётом) (флаг air)."""
        self.country: 'Country | None'
        """Объект страны, если был передан при инициализации."""
        self.produced_by: 'List[Factory] | None'
        """Фабрики, которые производят этот предмет (None если не привязан)."""
        self.id: str
        """Уникальный идентификатор предмета из БД items таблицы"""
        ...

    def edit_quantity(self, quantity: int, country: 'str | Country') -> None:
        """Изменяет количество предмета в инвентаре страны и сохраняет в БД.
        
        Обновляет значение как в локальном объекте, так и в базе данных.
        
        Args:
            quantity (int): Новое количество предмета.
            country (str | Country): Страна, для которой обновляется количество.
                Может быть строкой с названием или объектом Country.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRIES_PATH: таблица countries_inventory
                UPDATE {self.name} = {quantity} WHERE name = {country_name}
        """
        ...


class Market:
    """Представляет рынок конкретной страны для торговли предметами.
    
    Класс управляет коллекцией выставленных на продажу предметов, их количеством и ценой.
    При инициализации загружает данные из БД или создаёт новую запись для страны.
    Поддерживает операции добавления, изменения, удаления и получения предметов.
    
    Attributes:
        name (str): Название страны, чей рынок представлен.
        inventory (dict[str, Item]): Словарь предметов на рынке {название: Item}.
            Каждое значение содержит информацию о количестве и цене предмета.
    """

    def __init__(self, country: 'str | Country') -> None:
        """Инициализирует объект рынка для указанной страны.
        
        Если запись о рынке страны отсутствует в БД, она создаётся автоматически.
        Загружает все выставленные предметы с их количеством и ценами.
        
        Args:
            country (str | Country): Страна, для которой создаётся/загружается рынок.
                Может быть строкой с названием или объектом Country.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRIES_PATH: таблица market
                SELECT * WHERE name = {country_name}
                Если запись не найдена, создаёт новую со всеми полями как '0 0'
            
            Формат данных в БД:
            - Каждый столбец предмета содержит строку формата: "количество цена"
            - Парсится при инициализации в объекты Item
        """
        self.name: str
        """Название страны, чей рынок представлен."""
        self.inventory: dict[str, Item]
        """Словарь предметов на рынке {название: Item}. Каждое значение содержит информацию о количестве и цене."""
        ...

    def get_inv(self, quest: bool = False) -> dict:
        """Возвращает инвентарь рынка (словарь предметов).
        
        При необходимости можно включить предметы с нулевым количеством.
        
        Args:
            quest (bool): Если True, включаются все предметы, даже с нулевым количеством.
                Если False (по умолчанию), возвращаются только предметы с quantity > 0.
        
        Returns:
            dict[str, Item]: Словарь предметов на рынке {название: Item}.
        """
        ...

    def add_item(self, item: 'Item') -> None:
        """Добавляет новый предмет на рынок страны.
        
        Создаёт новую колонку в записи рынка в БД (если её нет) и добавляет
        предмет в локальный инвентарь рынка.
        
        Args:
            item (Item): Объект предмета для добавления на рынок.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRIES_PATH: таблица market
                INSERT INTO market (name, {item.name}) 
                VALUES ({self.name}, '{quantity} {price}')
        """
        ...

    def edit_item(self, item: 'Item') -> None:
        """Обновляет информацию о предмете на рынке (количество и цена).
        
        Если предмета ещё нет на рынке, добавляет его через add_item().
        Иначе обновляет его количество и цену в БД и локально.
        
        Args:
            item (Item): Объект предмета с новыми значениями quantity и price.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRIES_PATH: таблица market
                UPDATE market SET {item.name} = '{quantity} {price}' 
                WHERE name = {self.name}
        """
        ...

    def remove_item(self, item: 'Item | str') -> None:
        """Удаляет предмет с рынка, устанавливая его значение в "0 0".
        
        Предмет остаётся в записи БД, но становится недоступным для покупки.
        
        Args:
            item (Item | str): Объект предмета или его название (строка).
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRIES_PATH: таблица market
                UPDATE market SET {item_name} = '0 0' WHERE name = {self.name}
        """
        ...


class Factory:
    """Представляет тип фабрики в игре с её характеристиками производства.
    
    Класс используется для работы с производственными объектами: их производительностью,
    стоимостью, описанием и количеством в определённой стране. Данные о типе фабрики
    загружаются из БД, количество может быть привязано к стране.
    
    Attributes:
        name (str): Название фабрики.
        quantity (int): Количество фабрик данного типа в стране.
        country (Country | None): Объект страны, которой принадлежат фабрики (None если не привязана).
        produces (str): Ключ производимого предмета (например, название товара или 'Деньги').
        count (float): Количество единиц продукции, производимых одной фабрикой за период.
        desc (str): Описание и название фабрики.
        cost (int): Стоимость постройки одной единицы этой фабрики.
        max_size (int): Максимальное количество фабрик, которые можно построить прежде чем начнется убывающая отдача
        maintenance (int): Стоимость обслуживания одной единицы этой фабрики за период
        id (str): Уникальный идентификатор фабрики из БД factories таблицы
    """

    def __init__(self, factory_name: str, quantity: int | None = None, 
                 country: 'str | Country | None' = None) -> None:
        """Инициализирует объект фабрики.
        
        Если количество не указано, оно загружается из данных страны. Атрибуты фабрики
        (производимый товар, производительность, стоимость, описание) загружаются из БД.
        
        Args:
            factory_name (str): Название фабрики (должно соответствовать записи в БД).
            quantity (int | None): Количество фабрик. Если None, загружается из страны.
            country (str | Country | None): Страна, в которой находятся фабрики.
                Может быть строкой с названием или объектом Country.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRIES_PATH: таблица factories
                SELECT produces_key, count, desc, cost WHERE name = {factory_name}
        """
        self.name: str
        """Название фабрики."""
        self.quantity: int
        """Количество фабрик данного типа в стране."""
        self.country: 'Country | None'
        """Объект страны, которой принадлежат фабрики (None если не привязана)."""
        self.produces: str
        """Ключ производимого предмета (например, название товара или 'Деньги')."""
        self.count: float
        """Количество единиц продукции, производимых одной фабрикой за период."""
        self.desc: str
        """Описание и название фабрики."""
        self.cost: int
        """Стоимость постройки одной единицы этой фабрики."""
        self.max_size: int
        """Максимальное количество фабрик, которые можно построить прежде чем начнется убывающая отдача."""
        self.maintenance: int
        """Стоимость обслуживания одной единицы этой фабрики за период."""
        ...

    def edit_quantity(self, quantity: int, country: 'str | Country') -> None:
        """Изменяет количество фабрик данного типа в стране и сохраняет в БД.
        
        Обновляет значение как в локальном объекте, так и в базе данных.
        
        Args:
            quantity (int): Новое количество фабрик.
            country (str | Country): Страна, для которой обновляется количество.
                Может быть строкой с названием или объектом Country.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_COUNTRIES_PATH: таблица country_factories
                UPDATE {self.name} = {quantity} WHERE name = {country_name}
        """
        ...


class Focus:
    """Представляет национальный фокус (проект) страны с требованиями и наградами.
    
    Класс управляет национальными фокусами: их требованиями (предметы, фабрики, новости),
    наградами (предметы, фабрики, события), эмодзи и описанием. Фокусы образуют древо
    развития, где каждый фокус может требовать завершения предыдущего.
    
    Attributes:
        name (str): Название фокуса.
        description (str): Описание фокуса и его эффектов.
        emoji (str | None): Эмодзи, отображаемое рядом с названием фокуса (None если нет).
        owner (Country | None): Страна, владеющая этим фокусом (None если не привязан).
        req_items (List[Item] | None): Требуемые предметы для выполнения фокуса.
        req_factories (list[Factory] | None): Требуемые фабрики для выполнения фокуса.
        req_news (str | None): Требуется ли новостное сообщение для выполнения (None если нет).
        event (str | None): ID события, которое происходит при выполнении фокуса (None если нет).
        reward_items (List[Item] | None): Предметы, получаемые при завершении фокуса.
        reward_factories (list[Factory] | None): Фабрики, получаемые при завершении фокуса.
        building_slots_reward (int): Количество строительных ячеек, получаемых при завершении.
    """

    def __init__(self, name: str, owner: 'Country | None' = None) -> None:
        """Инициализирует объект национального фокуса.
        
        Загружает все данные фокуса из БД: требования, награды, описание, эмодзи.
        При необходимости создаёт объекты Item и Factory для требований и наград.
        
        Args:
            name (str): Название фокуса (должно соответствовать записи в БД).
            owner (Country | None): Страна-владелец этого фокуса. По умолчанию None.
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_FOCUS_PATH: таблица focuses
                SELECT name, desc, emoji, req_items, req_factories, req_news, event,
                       reward_items, reward_factories, building_slots_reward
                WHERE name = {name}
        """
        self.name: str
        """Название фокуса."""
        self.description: str
        """Описание фокуса и его эффектов."""
        self.emoji: 'str | None'
        """Эмодзи, отображаемое рядом с названием фокуса (None если нет)."""
        self.owner: 'Country | None'
        """Страна, владеющая этим фокусом (None если не привязан)."""
        self.req_items: 'List[Item] | None'
        """Требуемые предметы для выполнения фокуса."""
        self.req_factories: 'list[Factory] | None'
        """Требуемые фабрики для выполнения фокуса."""
        self.req_news: 'str | None'
        """Требуется ли новостное сообщение для выполнения (None если нет)."""
        self.event: 'str | None'
        """ID события, которое происходит при выполнении фокуса (None если нет)."""
        self.reward_items: 'List[Item] | None'
        """Предметы, получаемые при завершении фокуса."""
        self.reward_factories: 'list[Factory] | None'
        """Фабрики, получаемые при завершении фокуса."""
        self.building_slots_reward: int
        """Количество строительных ячеек, получаемых при завершении."""
        ...

    async def send_event(self) -> None:
        """Отправляет событие в соответствующий канал при выполнении фокуса.
        
        Если фокус имеет associated event, отправляет сообщение события в канал событий.
        
        Returns:
            None
        
        Note:
            Зависит от self.event (ID события в БД).
            Отправляет в канал для событий фокусов.
        """
        ...

    async def declare_war(self) -> None:
        """Объявляет войну (если это подходящий фокус войны).
        
        Создаёт новый форум для войны и отправляет уведомления.
        
        Returns:
            None
        """
        ...

    def send_factories(self) -> None:
        """Отправляет предметы-награды (фабрики) в инвентарь страны-владельца.
        
        Добавляет все reward_factories к текущему количеству в country_factories.
        
        Returns:
            None
        """
        ...

    def send_items(self) -> None:
        """Отправляет предметы-награды в инвентарь страны-владельца.
        
        Добавляет все reward_items к текущему количеству в countries_inventory.
        
        Returns:
            None
        """
        ...

    def requirements_complete(self) -> bool:
        """Проверяет, выполнены ли все требования фокуса для его запуска.
        
        Проверяет наличие требуемых предметов, фабрик и (если нужно) новостного сообщения.
        
        Returns:
            bool: True если все требования выполнены, False иначе.
        """
        ...

    def mark_as_completed(self, country_name: 'str | Country | None' = None, 
                         connect = None) -> None:
        """Помечает фокус как завершённый в БД и обновляет current фокус страны.
        
        Устанавливает doing фокус в current и очищает doing поле.
        При необходимости отправляет награды.
        
        Args:
            country_name (str | Country | None): Страна, для которой завершается фокус.
                Если None, использует self.owner.name.
            connect: Переиспользуемое подключение к БД (опционально).
        
        Returns:
            None
        
        Note:
            Используемые БД:
            - DATABASE_FOCUS_PATH: таблица countries
                UPDATE countries SET current = {doing}, doing = NULL
                WHERE name = {country_name}
        """
        ...

    @property
    def is_completed(self) -> bool:
        """Проверяет, завершён ли фокус для страны-владельца.
        
        Возвращает True если фокус находится в current_focus владельца.
        
        Returns:
            bool: True если фокус завершён, False иначе.
        """
        ...

    @is_completed.setter
    def is_completed(self, value: bool) -> None:
        """Устанавливает статус завершённости фокуса (вспомогательный метод).
        
        Args:
            value (bool): Значение для установки.
        
        Returns:
            None
        """
        ...

    async def complete_focus(self) -> None:
        """Полностью завершает фокус: проверяет требования, отправляет награды, обновляет БД.
        
        1. Проверяет выполнены ли requirements_complete()
        2. Отправляет все награды (предметы, фабрики, ячейки)
        3. Помечает фокус как завершённый
        4. Обновляет БД
        
        Returns:
            None
        
        Note:
            Вызывает: send_items(), send_factories(), increase_building_slots(),
                     mark_as_completed(), send_event(), declare_war()
        """
        ...


class ChooseMenu:
    """Пагинированное выпадающее меню с навигацией между страницами.
    
    Класс представляет собой Discord View с Select компонентом и кнопками навигации
    для пролистывания опций по страницам. Поддерживает вызов асинхронного callback
    при выборе опции.
    
    Поддерживает:
    - Пагинацию опций через кнопки ⏮️ (предыдущая) и ⏭️ (следующая)
    - Автоматическое обновление Select при смене страницы
    - Вызов callback функции при выборе опции
    - Защиту от быстрых нажатий через Lock
    - Отключение кнопок в конце/начале списка
    
    Attributes:
        values (dict[str, str]): Словарь {label: value} для отображения в Select.
        callback (Callable): Асинхронная функция вида: async def callback(interaction, selected_value)
        current_page (int): Текущая страница пагинации (начиная с 1).
        total_pages (int): Общее количество страниц.
        select (Select): Discord Select компонент с текущими опциями.
        message (Message | None): Ссылка на Discord сообщение с View (для обновления).
        lock (asyncio.Lock): Защита от одновременных операций.
    """

    def __init__(self, values: dict[str, str], callback: 'Callable[[Interaction, str], Awaitable[None]]') -> None:
        """Инициализирует меню выбора с пагинацией.
        
        Создаёт View с Select компонентом для первой страницы и кнопками навигации.
        Если опций нет, создаёт заглушку с отключённым Select.
        
        Args:
            values (dict[str, str]): Словарь {label: value} для отображения в Select.
            callback (Callable[[Interaction, str], Awaitable[None]]): Асинхронная функция 
                вида: async def callback(interaction: Interaction, selected_value: str)
        
        Returns:
            None
        
        Note:
            - timeout=None: меню существует пока не будет удалено сообщение
            - используется PAGE_SIZE из deps для разбиения опций на страницы
            - кнопки навигации автоматически отключаются на краях списка
        """
        ...

    def _create_select(self) -> 'Select':
        """Создаёт новый Select компонент с текущими опциями страницы.
        
        Используется при смене страницы для обновления доступных опций.
        Если на странице нет опций, создаёт заглушку с отключённым Select.
        
        Returns:
            Select: Discord Select компонент с опциями текущей страницы.
        """
        ...

    async def prev_button(self, interaction: 'Interaction', button: 'Button') -> None:
        """Обработчик кнопки предыдущей страницы (⏮️).
        
        Перемещает на одну страницу назад если это не первая страница.
        Использует lock для защиты от быстрых нажатий.
        
        Args:
            interaction (Interaction): Discord взаимодействие при нажатии кнопки.
            button (Button): Объект кнопки (не используется напрямую).
        
        Returns:
            None
        
        Note:
            - Если current_page <= 1: просто отклоняет взаимодействие
            - Вызывает _update_menu() для обновления View
        """
        ...

    async def next_button(self, interaction: 'Interaction', button: 'Button') -> None:
        """Обработчик кнопки следующей страницы (⏭️).
        
        Перемещает на одну страницу вперёд если это не последняя страница.
        Использует lock для защиты от быстрых нажатий.
        
        Args:
            interaction (Interaction): Discord взаимодействие при нажатии кнопки.
            button (Button): Объект кнопки (не используется напрямую).
        
        Returns:
            None
        
        Note:
            - Если current_page >= total_pages: просто отклоняет взаимодействие
            - Вызывает _update_menu() для обновления View
        """
        ...

    async def _update_menu(self, interaction: 'Interaction') -> None:
        """Обновляет Select и состояние кнопок при смене страницы.
        
        Загружает опции новой страницы, пересоздаёт Select компонент,
        обновляет состояние кнопок навигации (enabled/disabled).
        
        Args:
            interaction (Interaction): Discord взаимодействие для отправки обновления.
        
        Returns:
            None
        
        Note:
            - Если сообщение было удалено (NotFound), ошибка игнорируется
            - Автоматически отключает prev_button если current_page == 1
            - Автоматически отключает next_button если current_page >= total_pages
        """
        ...

    async def select_callback(self, interaction: 'Interaction', select: 'Select | None' = None) -> None:
        """Вызывается при выборе опции в Select.
        
        Извлекает выбранное значение и вызывает пользовательский callback.
        Поддерживает два способа вызова: через декоратор и через присвоение.
        
        Args:
            interaction (Interaction): Discord взаимодействие при выборе.
            select (Select | None): Select компонент (опционально, может быть None).
        
        Returns:
            None
        
        Note:
            - Безопасно обрабатывает оба способа получения выбранного значения
            - Если опции недоступны, отправляет ошибку пользователю
            - Вызывает self.callback с (interaction, selected_value)
        """
        ...

    async def on_timeout(self) -> None:
        """Отключает все компоненты View при истечении timeout.
        
        Вызывается автоматически через Discord.py при timeout View.
        Отключает все кнопки и Select, обновляет сообщение.
        
        Returns:
            None
        
        Note:
            - Если сообщение было удалено, ошибка игнорируется
            - Все компоненты становятся disabled для визуальной отчётливости
        """
        ...

class RpChannels:
    def __init__(self, event: int | TextChannel = '📣┃события', war: int | ForumChannel = '🔥┃войны', news: int | TextChannel = '📰┃новости-стран'):
        self.event = guild.get_role(event) if isinstance(event, int) else event
        self.war = guild.get_role(war) if isinstance(war, int) else war
        self.news = guild.get_role(news) if isinstance(news, int) else news
        
    def get_event(self) -> TextChannel:
        """Возвращает канал для ивентов"""
    async def set_event(self, event: int | str | TextChannel = '📣┃события'):
        """Присвает полю self.event новое значение"""
    async def del_event(self):
        """Пересоздает канал ивента"""
        
    def get_war(self) -> ForumChannel:
        """Возвращает канал для войн"""
    async def set_war(self, event: int | str | ForumChannel = '🔥┃войны'):
        """Присвает полю self.war новое значение"""
    async def del_war(self):
        """Пересоздает канал войн"""
        
    def get_news(self) -> TextChannel:
        """Возвращает канал для новостей"""
    async def set_news(self, event: int | str | TextChannel = '📰┃новости-стран'):
        """Присвает полю self.news новое значение"""
    async def del_news(self):
        """Пересоздает канал новостей"""

rp_channels: RpChannels