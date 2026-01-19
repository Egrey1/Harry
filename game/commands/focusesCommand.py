from ..library.modules import hybrid_command, Context, deps, View, Select, SelectOption
from ..callbacks import focus_callback
class FocusesCommand:
    @hybrid_command(name='focuses', description='Показать доступные национальные фокусы')
    async def focuses(self, ctx: Context):
        country = deps.Country(ctx.author.mention)
        if not country:
            await ctx.reply('Вы не страна!', ephemeral=True)
            return None

        available_focuses = country.give_available_focuses()
        if not available_focuses:
            await ctx.reply('У вас нет доступных фокусов!', ephemeral=True)
            return None

        view = View()
        # options = [SelectOption(label=focus.name, value=focus.name, emoji=focus.emoji) for focus in available_focuses]
        options = [SelectOption(label=focus.name, value=focus.name) for focus in available_focuses]
        select = Select(placeholder='Выберите фокус', options=options)
        select.callback = lambda interaction: focus_callback(interaction, country)
        view.add_item(select)

        await ctx.reply('Вам представлен список доступных фокусов', ephemeral=True, view=view)