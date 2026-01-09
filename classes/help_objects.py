from .library import View, Select, Button, ButtonStyle, Interaction, NotFound, Lock, get_options, button, select
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
        self.select = self._create_select()
        self.add_item(self.select)

        # Кнопки
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    def _create_select(self) -> Select:
        """Создаёт новый Select с текущими опциями."""
        return Select(
            placeholder=f"Выберите опцию (страница {self.current_page})",
            options=self.options,
            custom_id=f"choose_menu_select_{id(self)}"  # Уникальный ID, чтобы не было конфликтов
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
        self.add_item(self.select)

        # Обновляем состояние кнопок
        self.prev_button.disabled = self.current_page == 1
        self.next_button.disabled = self.current_page >= self.total_pages

        try:
            await interaction.response.edit_message(view=self)
        except NotFound:
            # Сообщение удалено — ничего не делаем
            pass

    @select(custom_id="choose_menu_select")  # Должно совпадать с тем, что в _create_select
    async def select_callback(self, interaction: Interaction, select: Select):
        """Вызывается при выборе опции."""
        selected_value = select.values[0]
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
