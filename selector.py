import discord
import discord.ui as ui
from discord.ext import commands
from config import DATABASE_ROLE_PICKER as DATABASE_PATH
from config import give_country
from config import RP_ROLES as roles_id
from sqlite3 import connect as con
from sqlite3 import Row



    

class SelectorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Возвращает словарь где говорит какие роли нужно ставить
    async def give_roles(self, name: str) -> dict:

        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(f"""
                       SELECT *
                       FROM roles 
                       WHERE name = '{name}'
                       """)
        result = cursor.fetchone()
        connect.close()
        if not result:
            return {}
        
        result = dict(result)
        result['const'] = [1353608772458905671, 1353894726847430766, 1358763645538009119, 1344519261216964710]
        return result
        


    # Возвращает кортеж всех доступных для регистрации стран
    async def give_all_countries(self) -> tuple:
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                        SELECT name
                        FROM roles
                        WHERE is_busy IS NULL and surrender IS NULL
                        """)
        result = tuple([row[0] for row in cursor.fetchall()])  
        connect.close()
        return result

    
    # Основная логика  файла
    async def picker_callback(self, interaction: discord.Interaction) -> None:
        country_name = ''.join(interaction.data['values']) 
        picker = await self.give_roles(country_name)
        await interaction.response.defer(ephemeral=True)

        # Меняем никнейм если у нас есть на это право
        try:
            user = interaction.user
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

        # Заносим пользователя в страну как занятого
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()
        cursor.execute(f"""
                       UPDATE roles
                       SET is_busy = '{user.mention}'
                       WHERE name = '{country_name}'
                       """) 
        connect.commit()
        connect.close()


    @commands.hybrid_command(name='reg', description='Зарегистрироваться за страну')
    async def send_role_picker(self, ctx: commands.Context) -> None:
        # Создаем сообщение со списком
        if not ctx.interaction:
            return

        countries = await self.give_all_countries()  
        options = []
        for country in countries:
            options.append(discord.SelectOption(label=country, value=country))
        
        view = ui.View()
        select = ui.Select(placeholder='Выберите страну', options=options)
        select.callback = self.picker_callback

        view.add_item(select)
        
        if ctx.interaction:
            if not options:
                await ctx.interaction.response.send_message("Увы, но доступных для регистрации стран нет", ephemeral= True)
                return None
            await ctx.interaction.response.send_message("Вам представлен список доступных для регистрации стран", view=view, ephemeral=True)
    
    @commands.hybrid_command(description='Снимает с вас регистрацию со страны')
    async def unreg(self, ctx: commands.Context) -> None:
        
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
        else:
            await ctx.send('Ожидайте снятия ролей, это не займет много времени')

        user = ctx.author
        for id in roles_id.values():
            try:
                role = ctx.guild.get_role(id) 
                await user.remove_roles(role) 
            except:
                continue
        unreg = ctx.guild.get_role(1344519330091503628)
        await user.add_roles(unreg)  
        try:
            await user.edit(nick='') 
        except:
            pass
        
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                        UPDATE roles
                        SET is_busy = null
                        WHERE is_busy = '{user.mention}'
                        """)
        connect.commit()

        connect.close()

        country = await give_country(ctx.author.mention)
        if not country:
            if ctx.interaction:
                await ctx.interaction.followup.send('Вы и так не были страной', ephemeral=True)
            return None

        if ctx.interaction:
            await ctx.interaction.followup.send('Вы больше не страна', ephemeral=True)
            return None
        await ctx.send('Вы больше не страна')
    
    @commands.Cog.listener()
    async def on_member_remove(self, user: discord.Member):
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                        UPDATE roles
                        SET is_busy = null
                        WHERE is_busy = '{user.mention}'
                        """)
        connect.commit()
        connect.close()



async def setup(bot: commands.Bot):
    await bot.add_cog(SelectorCog(bot))