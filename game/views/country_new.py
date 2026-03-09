from ..library import deps, View, Button, button, Interaction, Embed




def has_focus() -> bool:
    def dec(func):
        async def wrapper(self, interaction: Interaction, butt: Button | None = None, *args, **kwargs):
            # Проверяем наличие фокуса и требование новости
            if self.country.doing_focus is None or not self.country.doing_focus.req_news:
                if butt:
                    butt.disabled = True
                    butt.emoji = '❎'
                return
            return await func(self, interaction, butt, *args, **kwargs)
        wrapper.__wrapped__ = func
        return wrapper
    return dec

class CountryNewView(View):
    def __init__(self, country: deps.Country):
        super().__init__(timeout=None)  # Отключаем таймаут для постоянного использования
        self.country = country

        # Настроим состояние кнопки принятия фокуса (если она присутствует в children)
        for item in self.children:
            try:
                if getattr(item, 'label', None) == 'Принять фокус':
                    # Кнопка активна только если есть фокус И требуется новость
                    if self.country.doing_focus and self.country.doing_focus.req_news:
                        item.disabled = False
                    else:
                        item.disabled = True
            except Exception:
                pass

    async def return_new_button_callback(self, interaction: Interaction):
        await interaction.response.defer()
        if not (
            (interaction.user.resolved_permissions.administrator) or 
            ((deps.PERSONAL['curator'] in interaction.user.roles or deps.PERSONAL['zamcur'] in interaction.user.roles) and (deps.PERSONAL['politolog'] in interaction.user.roles)) or 
            (deps.PERSONAL['curpers'] in interaction.user.roles)
        ):
            await interaction.followup.send('У тебя нет на это прав!', ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        # Извлекаем текст футера безопасно
        footer_text = None
        if getattr(embed, 'footer', None):
            footer_text = getattr(embed.footer, 'text', None) or (embed.footer.get('text') if isinstance(embed.footer, dict) else None)
        country = deps.Country(footer_text or embed.footer) if footer_text else None
        
        if not country or not country.busy:
            await interaction.followup.send('Ошибка: не удалось определить страну!', ephemeral=True)
            return

        # Отправляем новость (send_news асинхронный)
        description = embed.description or ""
        await country.send_news(description, interaction.message.attachments, view=self)

        await interaction.message.delete()
    
    @button(label='Откатить', emoji='🔄')
    async def otkat(self, interaction: Interaction, _: Button):
        await interaction.response.defer()
        if (deps.PERSONAL['politolog'] not in interaction.user.roles) and (not interaction.user.resolved_permissions.administrator):
            await interaction.followup.send('У тебя нет права использовать эту кнопочку! Не тыкай сюда!', ephemeral=True)
            return

        country_name = interaction.message.author.display_name
        attachments = interaction.message.attachments
        attachments = [await file.to_file() for file in attachments]
        embed = Embed(title=f'🔄 Откат новости от {interaction.user.global_name}', description=interaction.message.content)
        embed.set_footer(text=country_name)

        return_new_view = View(timeout=None)  # Кнопка будет работать бесконечно
        return_new_button = Button(label='Отменить', emoji='🚫')
        return_new_button.callback = self.return_new_button_callback
        return_new_view.add_item(return_new_button)

        await deps.audit.send(embed=embed, view=return_new_view, files=attachments)

        await interaction.channel.send(content=f'🔄 Эй-эй! {country_name}, видимо, что-то нарушил и поэтому модератор {interaction.user.mention} откатил эту новость', delete_after=30)
        await interaction.message.delete()
    
    @button(label='Принять фокус', emoji='✅')
    @has_focus()
    async def accept_focus(self, interaction: Interaction, butt: Button):
        if (deps.PERSONAL['politolog'] not in interaction.user.roles) and (not interaction.user.resolved_permissions.administrator):
            await interaction.response.send_message('У тебя нет права использовать эту кнопочку! Не тыкай сюда!', ephemeral=True)
            return

        focus = self.country.doing_focus
        if not focus:
            await interaction.response.send_message('Фокус не найден!', ephemeral=True)
            return
            
        country = self.country  # Используем уже загруженную страну
        
        view = View()
        button = Button(label='Новость в тему фокуса', emoji='🗞️')
        button2 = Button(label='Новость не в тему фокуса', emoji='❌')
        
        # Создаём обработчики как методы, чтобы избежать проблем с захватом переменных
        async def button2_callback(inter: Interaction):
            await inter.response.send_message('Ты не в себе? Просто скрой мое предыдущее сообщение и все! Или откати, если страна неудачно пыталась выполнить этот фокус', ephemeral=True)
        
        async def button_callback(inter: Interaction):
            await self.focus_completed_callback(inter, focus)
        
        button2.callback = button2_callback
        button.callback = button_callback
        
        view.add_item(button)
        view.add_item(button2)

        embed = Embed(
            title=focus.name, 
            description=focus.description)
        embed.add_field(
            name='Требования фокуса', 
            value=focus.req_news or "Не требуется")
        embed.set_footer(text=country.name)

        await interaction.response.send_message(embed=embed, ephemeral=True, view=view)    
    
    async def focus_completed_callback(self, interaction: Interaction, focus: deps.Focus):
        if not focus.requirements_complete():
            await interaction.channel.send(f'{focus.owner.busy} попытался выполнить фокус `{focus.name}`, но он не выполнил все условия', delete_after=30)
            await interaction.response.defer(ephemeral=True)
            return
        focus.mark_as_completed()
        await interaction.response.send_message(f'Фокус успешно помечен как выполненный', ephemeral=True)