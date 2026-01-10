from ..library import Interaction, deps, Embed

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
    requirements_value_field = ('\n' if requirements_value_field else '') + '\nНужно отправлять новость? - ' + ('Да' if focus.req_news else 'Нет') 
    
    if requirements_value_field:
        embed.add_field(name="Требования", value="Сделать там вот так", inline=True)
    
    reward_value_field = '\n'.join([f"{factory.name}: {factory.quantity}шт." for factory in focus.factories])
    reward_value_field += ('\n' if reward_value_field else '') + '\n'.join([f"{item.name}: {item.quantity}шт." for item in focus.items])

    if reward_value_field:
        embed.add_field(name="Награда", value=reward_value_field, inline=True)
    
    war_value_field = ', '.join([f"{declare_country.name}" for declare_country in focus.war])

    if war_value_field:
        embed.add_field(name="Последствия", value="Объявление войны: " + war_value_field, inline=True)

    await interaction.response.send_message(content=f'Вы начали выполнение фокуса: **{focus.name}**', embed=embed, ephemeral=True)