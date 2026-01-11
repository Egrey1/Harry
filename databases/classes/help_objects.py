from .library import View, Select, Button, ButtonStyle, Interaction, NotFound, Lock, get_options, button
from discord import SelectOption
from typing import Dict, Callable, Awaitable

class ChooseMenu(View):
    """
    ## how to use? 
    ```
    async def on_choice_selected(interaction: Interaction, value: str):
        await interaction.response.send_message(f"You have chosen: `{value}`", 
                                                ephemeral=True)

    # Somewhere in the code...:
    values = {f"Country {i}": f"country_{i}" for i in range(1, 50)}
    view = ChooseMenu(values, on_choice_selected)
    view.message = await interaction.response.send_message(
        "Select country:", 
        view=view, 
        ephemeral=True
    )
    ```
    ⚠️ To make `view.message` work, you need to save a link to the message. In `discord.py`, you can do this:
    ```
    msg = await interaction.response.send_message("...", view=view)
    view.message = msg
    ```
    Пагинированное выпадающее меню с навигацией между страницами.
    
    Поддерживает пагинацию опций через кнопки ⏮️ и ⏭️.
    Обновляет Select при смене страницы.
    Вызывает callback при выборе опции.
    """
    def __init__(self, values: Dict[str, str], callback: Callable[[Interaction, str], Awaitable[None]]):
        """
        Инициализация меню выбора.
        
        :param values: Словарь {label: value} для отображения в Select.
        :param callback: Асинхронная функция вида: async def callback(interaction, selected_value)
        """
        super().__init__(timeout=None)
        self.values = values
        self.callback = callback
        self.current_page = 1
        self.lock = Lock()  # Защита от быстрых нажатий

        # Получаем данные для первой страницы
        self.options, self.total_pages = get_options(values, self.current_page)

        # Если список опций пуст — создаём заглушку, чтобы API не ругался
        if not self.options:
            placeholder_option = SelectOption(label="Нет опций", value="", description="", default=True)
            self.select = Select(placeholder=f"Выберите опцию (страница {self.current_page})", options=[placeholder_option], custom_id=f"choose_menu_select_{id(self)}", disabled=True)
        else:
            self.select = Select(placeholder=f"Выберите опцию (страница {self.current_page})", options=self.options, custom_id=f"choose_menu_select_{id(self)}")

        # Привязываем callback к динамическому Select
        self.select.callback = self.select_callback
        self.add_item(self.select)

        # Кнопки (они уже добавлены через декоратор @button, не добавляем их дважды)

    def _create_select(self) -> Select:
        """Создаёт новый Select с текущими опциями."""
        if not self.options:
            placeholder_option = SelectOption(label="Нет опций", value="", description="", default=True)
            return Select(placeholder=f"Выберите опцию (страница {self.current_page})", options=[placeholder_option], custom_id=f"choose_menu_select_{id(self)}", disabled=True)
        return Select(
            placeholder=f"Выберите опцию (страница {self.current_page})",
            options=self.options,
            custom_id=f"choose_menu_select_{id(self)}"
        )

    @button(label="⏮️", style=ButtonStyle.blurple, disabled=True)
    async def prev_button(self, interaction: Interaction, button: Button):
        async with self.lock:
            if self.current_page <= 1:
                await interaction.response.defer()
                return

            self.current_page -= 1
            await self._update_menu(interaction)

    @button(label="⏭️", style=ButtonStyle.blurple)
    async def next_button(self, interaction: Interaction, button: Button):
        async with self.lock:
            if self.current_page >= self.total_pages:
                await interaction.response.defer()
                return

            self.current_page += 1
            await self._update_menu(interaction)

    async def _update_menu(self, interaction: Interaction):
        """Обновляет Select и состояние кнопок."""
        self.options, _ = get_options(self.values, self.current_page)
        
        # Пересоздаём Select
        self.remove_item(self.select)
        self.select = self._create_select()
        # Привязываем callback к новому Select
        self.select.callback = self.select_callback
        self.add_item(self.select)

        # Обновляем состояние кнопок
        self.prev_button.disabled = self.current_page == 1
        self.next_button.disabled = self.current_page >= self.total_pages

        try:
            await interaction.response.edit_message(view=self)
        except NotFound:
            # Сообщение удалено — ничего не делаем
            pass

    async def select_callback(self, interaction: Interaction, select: Select | None = None):
        """Вызывается при выборе опции.

        Вызов может происходить двумя способами: через декоратор (framework передаёт select) или
        через присвоение `Select.callback` (тогда передаётся только `interaction`).
        Поэтому `select` здесь опционален.
        """
        # Получаем выбранное значение безопасно
        if select and getattr(select, 'values', None):
            selected_value = select.values[0]
        else:
            vals = interaction.data.get('values') if getattr(interaction, 'data', None) else None
            if not vals:
                await interaction.response.send_message('Похоже, опции недоступны.', ephemeral=True)
                return
            selected_value = vals[0]
        await self.callback(interaction, selected_value)

    async def on_timeout(self) -> None:
        """Отключает все компоненты при таймауте."""
        for item in self.children:
            item.disabled = True
        try:
            if self.message:
                await self.message.edit(view=self)
        except:
            pass
