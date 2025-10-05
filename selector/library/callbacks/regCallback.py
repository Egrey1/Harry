from ..modules import Interaction
from ..functions import give_roles, set_is_busy


# Основная логика  файла
async def picker_callback(interaction: Interaction) -> None:
    country_name = ''.join(interaction.data['values']) 
    picker = await give_roles(country_name)
    await interaction.response.defer(ephemeral=True)
    user = interaction.user
    
    try:
        # Меняем никнейм если у нас есть на это право
        try:
            await user.edit(nick=picker['nickname']) 
        except:
            await interaction.followup.send(f'Произошла ошибка при смене никнейма. Обратитесь в поддержку: {picker['nickname']}', ephemeral=True) # type: ignore
        
        # Создаем переменные всех неконстаных ролей с их ID
        sea = picker['sea']
        assembly = picker['assembly']

        # Выдаем стране константные значения
        for role_id in picker['const']:
            role = interaction.guild.get_role(role_id)  
            await user.add_roles(role) 

        # Выдаем все необходимые роли
        for i in (sea, assembly):
            if i:
                role = interaction.guild.get_role(i) 
                await user.add_roles(role) 

        # Отзываем ожидание
        await interaction.followup.send(
            "Роли успешно выданы!", 
            ephemeral=True
        ) 

        # Снимаем с пользователя роль незарегистрированного
        try:
            await user.remove_roles(interaction.guild.get_role(1344519330091503628))  
        except:
            pass
    except:
        pass

    await set_is_busy(user.mention, country_name)