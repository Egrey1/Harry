from .library.modules import (hybrid_command, describe, Context, Member, View, Select, SelectOption, deps)
from .library.callbacks import give_callback, use_callback

class GiveCommand:
    @hybrid_command (name= 'give', description='Передать вооружение стране')
    @describe(member='Кому передать')
    async def give(self, ctx: Context, member: Member):
        if not deps.game_state['game_started']:
            return
        
        # Получаем названия их стран если они ими являются
        country1 = deps.Country(ctx.author.mention)
        country2 = deps.Country(member.mention)

		# Проверяем,являются ли пользователи странами 
        if country1.busy:
            await ctx.send('Вы не страна!', ephemeral= True)
            return None
        
        if country2.busy:
            await ctx.send('Он не страна!', ephemeral= True)
            return None
        
        # Создаем список предметов 
        inv = country1.inventory
        options = []
        for name, item in inv.items():
            item: deps.Item
            if name != 'name' and item.purchasable and item.quantity:
                options.append(SelectOption(label=f'{name} - {item.quantity}шт.', value=name))


        # Создаем объект 
        view = View()
        select = Select(placeholder='Выберите товар', options=options)
        select.callback = lambda interaction: give_callback(interaction, country1, country2)

		# Отправляем сообщение. Если была введена слеш команда, то отправляем только ему()
        view.add_item(select)
        await ctx.send('Выберите что хотите передать' + ', но только тихо....' if ctx.interaction else '', ephemeral= True, view= view)


class UseCommand:
    @hybrid_command(name='use', description='Убрать предмет')
    async def use(self, ctx: Context) -> None:
        country = deps.Country(ctx.author.mention)
        if not country:
            await ctx.reply('Вы не страна!', ephemeral=True)
            return None

        inv = country.inventory
        options = []
        for name, count in inv.items():
            if name not in ('name') and int(count):
                options.append(SelectOption(label=f'{name} - {int(count)}шт.', value=name))
        
        view = View()
        select = Select(placeholder='Выберите товар', options=options)
        select.callback = lambda interaction: use_callback(interaction, country)
        view.add_item(select)

        await ctx.send('Что должно испариться?', view= view, ephemeral=True)
        
