from ..library import deps, View, Button, button, Interaction, Embed




def has_focus() -> bool:
    def dec(func):
        async def wrapper(self, interaction: Interaction, butt: Button | None = None, *args, **kwargs):
            if self.country.doing_focus is None:
                butt.disabled = True
                butt.emoji = '❎'
                return
            return await func(self, interaction, butt, *args, **kwargs)
        wrapper.__wrapped__ = func
        return wrapper
    return dec

class CountryNewView(View):
    def __init__(self, country: deps.Country):
        super().__init__()
        self.country = country

        # Настроим состояние кнопки принятия фокуса (если она присутствует в children)
        for item in self.children:
            try:
                if getattr(item, 'label', None) == 'Принять фокус':
                    item.disabled = not bool(self.country.doing_focus)
            except Exception:
                pass

    async def return_new_button_callback(self, interaction: Interaction):
        interaction.response.defer()
        if (
        (interaction.user.resolved_permissions.administrator) and 
        ((deps.PERSONAL['curator'] in interaction.user.roles or deps.PERSONAL['zamcur'] in interaction.user.roles) and (deps.PERSONAL['politolog'] in interaction.user.roles)) and 
        (deps.PERSONAL['curpers'] in interaction.user.roles)):
            await interaction.followup.send('У тебя нет на это прав!', ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        # Извлекаем текст футера безопасно
        footer_text = None
        if getattr(embed, 'footer', None):
            footer_text = getattr(embed.footer, 'text', None) or (embed.footer.get('text') if isinstance(embed.footer, dict) else None)
        country = deps.Country(footer_text or embed.footer)

        # Отправляем новость (send_news асинхронный)
        await country.send_news(embed.description, interaction.message.attachments, view=self)

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

        return_new_view = View()
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
        country = deps.Country(interaction.message.author.display_name)
        if not focus.requirements_complete():
            await interaction.message.channel.send(f'{country.busy} попытался выполнить фокус `{focus.name}`, но он не выполнил все условия', delete_after=30)
            return
        
        focus.mark_as_completed()
        await interaction.response.send_message(f'Фокус успешно помечен как выполненный', ephemeral=True)

        # butt.disabled = True
        # await interaction.message.edit(view=self)    