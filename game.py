from discord import Member
from discord.ui import Modal, TextInput, View, Select
from discord.ext import commands

from sqlite3 import connect as con
from sqlite3 import Row

from config import CURRENCY, give_country, GUILD
from config import RP_ROLES as roles_id
from config import DATABASE_COUNTRIES as DATABASE_COUNTRIES_PATH
from config import DATABASE_ROLE_PICKER as DATABASE_ROLE_PICKER_PATH

class ShopCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild = bot.get_guild(GUILD)
    
    async def unreg_function(self, member: Member):
        for id in roles_id.values():
            try:

                role = self.guild.get_role(id) 
                await member.remove_roles(role) 
            except:
                continue
        unreg = self.guild.get_role(1344519330091503628)
        await member.add_roles(unreg)  
        try:
            await member.edit(nick='') 
        except:
            pass
        
        connect = con(DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                        UPDATE roles
                        SET is_busy = null
                        WHERE is_busy = '{member.mention}'
                        """)
        connect.commit()

        connect.close()

    @commands.hybrid_command(description='Начинает или заканчивает вайп')
    @commands.has_permissions(administrator=True)
    async def vipe(self, ctx: commands.Context):
        connect = con(DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                       SELECT is_busy
                       FROM roles
                       WHERE is_busy IS NOT NULL
                       """)
        result = cursor.fetchall()
        connect.close()

        for member in result:
            self.unreg_function(self.guild.get_member(int(member[2:-1])))

        




async def setup(bot):
    await bot.add_cog(ShopCog(bot))