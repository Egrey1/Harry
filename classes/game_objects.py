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
    def __init__(self, id_: str = 'ITA'):
        self.busy = None
        self.is_country = True

        # Если передано упоминание
        if id_.startswith('<@') and id_.endswith('>'):
            conn = con(deps.DATABASE_ROLE_PICKER_PATH)
            cursor = conn.cursor()
            
            cursor.execute(f"""
                            SELECT name, id
                            FROM roles
                            WHERE is_busy = '{id_}'
            """)
            result = cursor.fetchone()
            conn.close()
            if result:
                self.name = result[0]
                id_ = result[1]
            else:
                self.is_country = False
                return
        # Если передано название страны или ее id
        else:
            connect = con(deps.DATABASE_ROLE_PICKER_PATH)
            cursor = connect.cursor()

            cursor.execute("""
                           SELECT id
                           FROM roles
                           WHERE name = ?
                           """, (id_, ))
            fetch = cursor.fetchone()
            connect.close()
            if fetch:
                self.name = id_
                id_ = fetch[0]
            # Если передано id
            else:
                connect = con(deps.DATABASE_ROLE_PICKER_PATH)
                cursor = connect.cursor()

                cursor.execute("""
                               SELECT name
                               FROM roles
                               WHERE id = ?
                               """, (id_, ))
                fetch = cursor.fetchone()
                connect.close()
                if fetch:
                    self.name = fetch[0]
                else:
                    self.is_country = False
                    return

        
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute(f"""
                        SELECT *
                        FROM countries_inventory
                        WHERE country_id = '{id_}'
                        """)
        inventory_fetch = cursor.fetchone()

        cursor.execute(f"""
                        SELECT *
                        FROM country_factories
                        WHERE country_id = '{id_}'
                        """)
        factories_fetch = cursor.fetchone()
        connect.close()

        self.id = id_
        self.market = Market(self)

        self.inventory: dict[str, Item] = {}
        self.factories: dict[str, Factory] = {}
        self.balance: int = 0

        for i in inventory_fetch.keys():
            if i != 'country_id' and i != 'Деньги':
                self.inventory[i] = Item(i, int(inventory_fetch[i]), country=self)
        
        for i in factories_fetch.keys():
            if i != 'country_id':
                self.factories[i] = Factory(i, int(factories_fetch[i]), country=self)
        
        self.balance = int(inventory_fetch['Деньги'])

        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        
        cursor.execute(f"""
                        SELECT *
                        FROM roles
                        WHERE id = '{self.id}'
                        """)
        fetch = dict(cursor.fetchone())
        connect.close()
        
        self.busy = deps.guild.get_member(int(fetch['is_busy'][2:-1])) if fetch and fetch['is_busy'] else None
        self.surrend = bool(fetch['surrender']) if fetch else False
        self.sea = deps.guild.get_role(int(fetch['sea'])) if fetch and fetch['sea'] else None
        self.assembly = deps.guild.get_role(int(fetch['assembly'])) if fetch and fetch['assembly'] else None
        self.nickname = fetch['nickname'] if fetch and fetch['nickname'] is not None else ""

        
        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT doing, current
                        FROM countries
                        WHERE country_id = '{self.id}'
                        """)
        fetch = cursor.fetchone()
        cursor.close()

        self.doing_focus: Focus | None = None
        self.current_focus: Focus | None = None
        
        if fetch:
            self.doing_focus = Focus(fetch[0], self) if fetch[0] else None
            self.current_focus = Focus(fetch[1], self) if fetch[1] else None
        
        # Загружаем информацию о строительных ячейках
        self.building_slots = self._load_building_slots()
    
    def _load_building_slots(self) -> int:
        try:
            connect = con(deps.DATABASE_COUNTRY_AI_PATH)
            cursor = connect.cursor()
            cursor.execute("""
                            SELECT building_slots
                            FROM country_info
                            WHERE country_id = ?
                            """, (self.id,))
            fetch = cursor.fetchone()
            connect.close()
            
            if fetch:
                return int(fetch[0])
            else:
                # Нет записи в БД - логируем ошибку
                import logging
                logging.error(f'Нет записи country_info для {self.name}')
                if deps.audit:
                    try:
                        from discord import Embed
                        embed = Embed(title='⚠️ Ошибка загрузки building_slots', 
                                    description=f'Нет записи country_info для {self.name}',
                                    color=0xFF0000)
                        deps.audit.send(embed=embed)
                    except:
                        pass
                return 0
        except Exception as e:
            import logging
            logging.error(f'Ошибка при загрузке building_slots для {self.name}: {e}')
            if deps.audit:
                try:
                    from discord import Embed
                    embed = Embed(title='⚠️ Ошибка загрузки building_slots', 
                                description=f'{self.name}: {str(e)}',
                                color=0xFF0000)
                    deps.audit.send(embed=embed)
                except:
                    pass
            return 0
    
    def get_used_building_slots(self) -> int:
        total = 0
        for factory in self.factories.values():
            if factory.name != 'Коммерческая зона': # ВРЕМЕННО! НАДО ИСПРАВИТЬ!
                total += factory.quantity
        return total
    
    def get_available_building_slots(self) -> int:
        return self.building_slots - self.get_used_building_slots()
    
    def increase_building_slots(self, amount: int) -> bool:
        new_slots = self.building_slots + amount
        used_slots = self.get_used_building_slots()
        
        # Гарантируем, что новый лимит не меньше текущего количества фабрик
        if new_slots < used_slots:
            import logging
            logging.warning(f'Попытка установить building_slots={new_slots} для {self.name}, но используется {used_slots}. Устанавливаем минимум {used_slots}.')
            new_slots = used_slots
        
        try:
            connect = con(deps.DATABASE_COUNTRY_AI_PATH)
            cursor = connect.cursor()
            cursor.execute("""
                            UPDATE country_info
                            SET building_slots = ?
                            WHERE country_id = ?
                            """, (new_slots, self.id))
            connect.commit()
            connect.close()
            
            # Обновляем локальное значение
            self.building_slots = new_slots
            return True
        except Exception as e:
            import logging
            logging.error(f'Ошибка при увеличении building_slots для {self.name}: {e}')
            if deps.audit:
                try:
                    from discord import Embed
                    embed = Embed(title='⚠️ Ошибка увеличения building_slots', 
                                description=f'{self.name}: {str(e)}',
                                color=0xFF0000)
                    deps.audit.send(embed=embed)
                except:
                    pass
            return False
    
    def __str__(self):
        return self.name

    async def change_surrend(self, interaction: Interaction | None = None):
        country = Country(interaction.data['values'][0]) if interaction else self
        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()
        
        if self.surrend:
            cursor.execute(f"""
                            UPDATE roles
                            SET surrender = NULL
                            WHERE country_id = '{country.id}'
            """)
            self.surrend = False
            connect.commit()
            connect.close()
            await self.unreg(interaction) 
        else:
            cursor.execute(f"""
                            UPDATE roles
                            SET surrender = '1'
                            WHERE country_id = '{self.id}'
            """)
            self.surrend = True
            connect.commit()
            connect.close()

    async def change_nickname(self, new_nickname: str):
        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                       UPDATE roles
                       SET nickname = '{new_nickname}'
                       WHERE country_id = '{self.id}'
                       """)
        connect.commit()
        connect.close()
        
        if self.busy:
            try:
                await self.busy.edit(nick=new_nickname)
            except:
                pass  # Игнорируем ошибки изменения никнейма -> translate: Ignore

    async def unreg(self, interaction: Interaction | Context | None = None):
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

        cursor.execute("""
                        UPDATE roles
                        SET is_busy = NULL
                        WHERE is_busy = ?
                        """, (self.busy.mention,))
        
        connect.commit()
        connect.close()
        self.busy = None

    async def send_news(self, news: str, attachments: List[Attachment], view):
        files = [await file.to_file() for file in attachments]
        channel = deps.guild.get_channel(1429571616982958222)

        # Попытка загрузить аватар из БД
        avatar_bytes = None
        # try:
        conn = con(deps.DATABASE_COUNTRY_AI_PATH)
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT avatar 
                        FROM avatars 
                        WHERE country_id = ?""", (self.id,))
        row = cursor.fetchone()
        conn.close()
        avatar_bytes = row[0] if row and row[0] else None
        # except Exception:
        #     avatar_bytes = None

        try:
            # Если нет аватара, попробуем использовать первый доступный вебхук
            if not avatar_bytes:
                webhooks = await channel.webhooks()
                if webhooks:
                    await webhooks[0].send(content=news, username=self.name, files=files, view=view)
                    return

            # Создаём временный вебхук (с аватаром, если он есть) и отправляем сообщение
            if avatar_bytes:
                webhook = await channel.create_webhook(name=self.name, avatar=avatar_bytes)
            else:
                webhook = await channel.create_webhook(name=self.name)

            await webhook.send(content=news, username=self.name, files=files, view=view)
        finally:
            # Удаляем временный вебхук, если он был создан
            try:
                if 'webhook' in locals():
                    await webhook.delete()
            except Exception:
                pass
                
    def give_available_focuses(self) -> list['Focus']:
        if not self.current_focus:
            return []
        
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
                          WHERE country_id = '{self.id}'
                        """)
        connect.commit()
        connect.close()
        self.doing_focus = focus if isinstance(focus, Focus) else Focus(focus, self)
    
    def get_expenses(self) -> int:
        total_expenses = 0
        for factory in self.factories.values():
            total_expenses += factory.maintenance * factory.quantity
        return total_expenses
    
    def get_earnings(self) -> int:
        total_earnings = 0
        for factory in self.factories.values():
            if factory.produces == 'Деньги':
                total_earnings += factory.count * factory.quantity
        return total_earnings

class Item:
    def __init__(self, name: str, quantity: int | None = None, price: int = 0, country: str | Country | None = None):
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
        fetch = cursor.fetchone()
        if not fetch:
            cursor.execute(f"""
                           SELECT *
                           FROM items
                           WHERE id = ?
                           """, (name, ))
            fetch = cursor.fetchone()

        items_info = dict(fetch)
        name = items_info['name']

        if items_info is None:
            raise ValueError(f"Предмет с именем '{name}' не найдена в базе данных.")
        
        self.purchasable = int(items_info['tradable']) == 1
        self.is_ship = int(items_info['ship']) == 1
        self.is_ground = int(items_info['ground']) == 1
        self.is_air = int(items_info['air']) == 1
        self.id = items_info['id']

        cursor.execute(f"""
                        SELECT name
                        FROM factories
                        WHERE produces_key = '{self.name}'
                       """)
        
        fetchs = cursor.fetchall()
        connect.close()

        self.produced_by: List[Factory] | None = None if (not fetchs) or (not self.country) else []
        if isinstance(self.produced_by, list):
            for fetch in fetchs:
                self.produced_by.append(Factory(fetch['name'], country=self.country))

    def edit_quantity(self, quantity: int, country: str | Country) -> None:
        country = Country(country) if not isinstance(country, Country) else country
        country_id = country.id
        self.quantity = quantity
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        UPDATE countries_inventory
                        SET `{self.name}` = {quantity}
                        WHERE `country_id` = '{country_id}'
        """)
        connect.commit()
        connect.close()


class Market:
    def __init__(self, country: str | Country):
        self.country = Country(country) if not isinstance(country, Country) else country

        self.name = country.name
        self.inventory: dict[str, Item] = {}

        connect = con(deps.DATABASE_COUNTRIES_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        try:
            cursor.execute(f"""
                SELECT *
                FROM market
                WHERE country_id = '{country.id}'
            """)
        except:
            # Если таблица или запись не существует, создаём запись
            cursor.execute(f"""
                INSERT INTO market (country_id)
                VALUES ('{country.id}')
            """)
            connect.commit()

            cursor.execute(f"""
                SELECT *
                FROM market
                WHERE country_id = '{country.id}'
            """)
        
        fetch = cursor.fetchone()
        if not fetch:
            cursor.execute(f"""
                INSERT INTO market (country_id)
                VALUES ('{country.id}')
            """)
            connect.commit()

            cursor.execute(f"""
                SELECT *
                FROM market
                WHERE country_id = '{country.id}'
            """)
            fetch = cursor.fetchone()
        
        result = dict(fetch)
        connect.close()

        # Парсим поля: каждое поле (кроме 'name') содержит строку вида "количество цена"
        for name, value in result.items():
            if name != 'country_id' and value:
                parts = value.split()
                quantity = int(parts[0]) if len(parts) > 0 else 0
                price = int(parts[1]) if len(parts) > 1 else 0
                self.inventory[name] = Item(name, quantity, price)

    def get_inv(self, quest: bool = False) -> dict:
        result = {}
        for name, item in self.inventory.items():
            if item.quantity > 0 or quest:
                result[name] = item
        return result

    def add_item(self, item: Item) -> None:
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
            INSERT INTO market (country_id, `{item.name}`)
            VALUES ('{self.country.id}', '{item.quantity} {item.price}')
        """)
        connect.commit()
        connect.close()
        self.inventory[item.name] = item

    def edit_item(self, item: Item) -> None:
        if item.name not in self.inventory:
            self.add_item(item)
            return None

        self.inventory[item.name] = item
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
            UPDATE market
            SET `{item.name}` = '{item.quantity} {item.price}'
            WHERE country_id = '{self.country.id}'
        """)
        connect.commit()
        connect.close()

    def remove_item(self, item: Item | str) -> None:
        item_name = item.name if isinstance(item, Item) else item
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
            UPDATE market
            SET `{item_name}` = '0 0'
            WHERE country_id = '{self.country.id}'
        """)
        connect.commit()
        connect.close()


class Factory:
    def __init__(self, factory_name: str, quantity: int | None = None, country: str | Country | None = None):
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
        if not fetch:
            print(country)
            cursor.execute("""
                           SELECT *
                           FROM factories
                           WHERE id = ?
                           """, (factory_name, ))
            fetch = cursor.fetchone()
            self.name = fetch['name']
            factory_name = self.name
        connect.close()

        if fetch is None:
            raise ValueError(f"Фабрика с именем '{factory_name}' не найдена в базе данных.")

        self.produces = fetch['produces_key']
        self.count = float(fetch['count'])
        self.desc = fetch['desc']
        self.cost = int(fetch['cost'])
        self.max_size = int(fetch['max_size'])
        self.maintenance = int(fetch['maintenance'])

    def edit_quantity(self, quantity: int, country: str | Country) -> None:
        country = Country(country) if not isinstance(country, Country) else country
        self.quantity = quantity
        connect = con(deps.DATABASE_COUNTRIES_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        UPDATE country_factories
                        SET `{self.name}` = {quantity}
                        WHERE `country_id` = '{country.id}'
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

        self.req_news: str | None = fetch['req_news'] if fetch['req_news'] else None
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

        await deps.rp_channels.get_event().send(text)
    
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
            self.owner.increase_building_slots(factory.quantity)
    
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
    
    def mark_as_completed(self, country_name: str | Country | None = None, connect=None):
        country = Country(country)if isinstance(country_name, str) else (country if isinstance(country_name, Country) else self.owner)
        own_connect = connect is None
        if own_connect:
            connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()
        
        cursor.execute("""
                        UPDATE countries
                        SET completed = ?
                        WHERE country_id = ?
                        """, (self.name, country.id))
        if own_connect:
            connect.commit()
            connect.close()
    
    @property
    def is_completed(self) -> bool:
        """Возвращает bool значение. True если фокус за страну выполнен и False, если self.owner не указзан или фокус не выполнен"""
        if self.owner is None:
            return False
        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()
        
        cursor.execute("""
                        SELECT doing, completed
                        from countries
                        WHERE country_id = ?
                        """, (self.owner.id,))
        doing, completed = cursor.fetchone()
        connect.close()
        
        if doing != completed or completed != self.name or completed is None:
            return False
        return True
    
    @is_completed.setter
    def is_completed(self, new_value: bool):
        
        if self.owner is None:
            return
        
        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()
        
        cursor.execute("""
                        UPDATE countries
                        SET completed = ?
                        WHERE country_id = ?
        """, (self.name if new_value else None, self.owner.id))
        connect.commit()
        connect.close()
    
    async def complete_focus(self):
        self.send_factories()
        self.send_items()
        await self.send_event()
        await self.declare_war()
        await self.send_event()
        await self.declare_war()

