from ..library import Interaction, deps, Embed, View, Select, SelectOption, Button

async def accepted(interaction: Interaction, country: deps.Country):
    focus = deps.Focus(interaction.data['values'][0], country)
    country.set_focus(focus)
    interaction.response.send_message(content=f'Вы выполняете фокус: **{focus.name}**', ephemeral=True)


async def focus_callback(interaction: Interaction, country: deps.Country):
    focus = deps.Focus(interaction.data['values'][0])
    
    embed = Embed(title=focus.name,
                  description=focus.description)
    
    requirements_value_field = '\n'.join([f"{factory.name} - {factory.quantity}шт." for factory in focus.req_factories])
    requirements_value_field += ('\n' if requirements_value_field else '') + '\n'.join([f"{item.name} - {item.quantity}шт." for item in focus.req_items])
    requirements_value_field += ('\n' if requirements_value_field else '') + ('\n' + focus.req_news if focus.req_news is not None else '') 
    
    if requirements_value_field:
        embed.add_field(name="Требования", value=requirements_value_field, inline=True)
    
    reward_value_field = '\n'.join([f"{factory.name}: {factory.quantity}шт." for factory in focus.factories])
    reward_value_field += ('\n' if reward_value_field else '') + '\n'.join([f"{item.name}: {item.quantity}шт." for item in focus.items])

    if reward_value_field:
        embed.add_field(name="Награда", value=reward_value_field, inline=True)
    
    war_value_field = ', '.join([f"{declare_country.name}" for declare_country in focus.war])

    if war_value_field:
        embed.add_field(name="Последствия", value="Объявление войны: " + war_value_field, inline=True)
        
    available_focuses = country.give_available_focuses()
    view = View()
    options = [SelectOption(label=focuss.name, value=focuss.name, emoji=focuss.emoji if focuss.emoji else None ) for focuss in available_focuses if focuss.name != focus.name]
    if options:
        select = Select(placeholder='Выберите фокус', options=options)
        select.callback = lambda interaction: focus_callback(interaction, country)
        view.add_item(select)
    select2 = Button(label= 'Принять', emoji='❎' if country.doing_focus is not None else '✅️', disabled= country.doing_focus is not None)
    select2.callback = lambda inter: accepted(inter, country)
    view.add_item(select2)

    await interaction.response.send_message(embed=embed, ephemeral=True, view=view)