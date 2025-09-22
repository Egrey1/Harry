import discord
import discord.ui as ui
from discord.ext import commands
from config import DATABASE_COUNTRIES as DATABASE_COUNTRIES_PATH
from config import DATABASE_ROLE_PICKER as DATABASE_ROLE_PICKER_PATH
from config import CURRENCY, give_country, get_money
from sqlite3 import connect as con, Row


class InventoryCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    
    # Возвращает весь инвентарь страны в виде словаря
    async def inventory_list(self, country: str) -> dict:
        connect = con(DATABASE_COUNTRIES_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(f"""
                       SELECT *
                       FROM countries_inventory
                       WHERE name = '{country}'
                       """)
        result = cursor.fetchone()
        connect.close()
        return dict(result) if result else {}
    
    # Возвращает все фабрики страны в виде словаря
    async def factory_list(self, country: str) -> dict:
        connect = con(DATABASE_COUNTRIES_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(f"""
                       SELECT *
                       FROM country_factories
                       WHERE name = '{country}'
                       """)
        result = cursor.fetchone()
        connect.close()
        return dict(result) if result else {}

    # Показывает всю армию страны и ее баланс
    async def give_army(self, interaction: discord.Interaction) -> None:
        country = await give_country(interaction.user.mention)
        await interaction.response.defer(ephemeral=True)

        if not country:
            await interaction.followup.send('Балван! Ты не страна! Ну или это ошибке в базе...', ephemeral=True)
            return None
        
        inv = await self.inventory_list(country)
        embed_desc = ''

        for key, value in inv.items():
            
            if key not in ('name', 'Деньги') and int(value):
                embed_desc += key + ' - ' + str(int(value)) + '\n\n'
        
        embed = discord.Embed(title=f'Баланс: {CURRENCY}{inv['Деньги']}', description=embed_desc)
        await interaction.followup.send(embed=embed, ephemeral=True)


    # Показывает все фабрики страны и ее баланс
    async def give_enterprise(self, interaction: discord.Interaction) -> None:
        country = await give_country(interaction.user.mention)
        await interaction.response.defer(ephemeral=True)

        if not country:
            await interaction.followup.send('Балван! Ты не страна! Ну или это ошибке в базе...', ephemeral=True)
            return None
        
        inv = await self.factory_list(country)
        embed_desc = ''

        for key, value in inv.items():
            
            if key != 'name' and int(value):
                embed_desc += key + ' - ' + str(int(value)) + '\n\n'
        
        embed = discord.Embed(title=f'Баланс: {CURRENCY}{await get_money(country)}', description=embed_desc)
        await interaction.followup.send(embed=embed, ephemeral=True)


	# Показывает инвентарь страны 
    @commands.command()
    async def inv(self, ctx: commands.Context):
        view = ui.View()
        army = ui.Button(label='Армия', emoji='🪖')
        enterprise = ui.Button(label='Предприятия', emoji='🏭')
        army.callback = self.give_army
        enterprise.callback = self.give_enterprise

        view.add_item(army)
        view.add_item(enterprise)
        await ctx.reply(f'`{await give_country(ctx.author.mention) if await give_country(ctx.author.mention) else ctx.author.nick}` конкрентизируйте', view=view, ephemeral=True)



    
    


async def setup(bot):
    await bot.add_cog(InventoryCog(bot))