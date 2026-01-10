from ..library.modules import (hybrid_command, describe, Context, Member, View, Select, SelectOption,
                               deps)
from ..library.callbacks import give_callback

class GiveCommand:
    @hybrid_command (name= 'give', description='Передать вооружение стране')
    @describe(member='Кому передать')
    async def give(self, ctx: Context, member: Member):
        if not deps.game_state['game_started']:
            return
        
        # Получаем названия их стран если они ими являются
        country1 = deps.Country(ctx.author.mention)
        country2 = deps.Country(member.mention)
        
        # Это слеш команда?
        is_interaction = bool(ctx.interaction)
        interaction = None
        if is_interaction:
            interaction = ctx.interaction

		# Проверяем,являются ли пользователи странами 
        if not country1:
            if is_interaction:
                await interaction.followup.send('Вы не страна!', ephemeral= True) 
                return None
            await ctx.send('Вы не страна!')
            return None
        elif not country2:
            if is_interaction:
                await interaction.followup.send('Он не страна!', ephemeral= True) 
                return None
            await ctx.send('Он не страна!')
            return None
        
        # Создаем список предметов 
        inv = country1.inventory
        options = []
        for name, item in inv.items():
            if item.purchasable and item.quantity:
                options.append(SelectOption(label=f'{name} - {int(item.quantity)}шт.', value=name))
                


        # Создаем объект 
        view = View()
        select = Select(placeholder='Выберите товар', options=options)
        select.callback = lambda interaction: give_callback(interaction, country1, country2)

		# Отправляем сообщение. Если была введена слеш команда, то отправляем только ему
        view.add_item(select)
        if is_interaction:
            await interaction.response.send_message('Выберите что хотите передать, но только тихо....', ephemeral= True, view= view)
        else:
            await ctx.send('Выберите что передать', view= view)