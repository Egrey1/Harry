from discord.ext import commands, tasks
from config import DATABASE_COUNTRIES as DATABASE_PATH
from config import game_state
from sqlite3 import connect as con
from sqlite3 import Row



    

class UpdaterCog(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.update_inventories.start()
    
    def cod_unload(self):
        self.update_inventories.cancel()

    
    async def give_factories(self) -> tuple[dict[str, any], ...]:
        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()


        cursor.execute(f"""
                    SELECT *
                    FROM country_factories
                    """)
        a = cursor.fetchall()
        connect.close()

        result = []
        for i in a:
            result.append(dict(i)) 
        return result

    # @tasks.loop(hours=1)
    @tasks.loop(seconds=10) # for test
    async def update_inventories(self):
        if not game_state['game_started']:
            return
        
        print('Инвентарь обновляется')
        connect = con(DATABASE_PATH)
        cursor = connect.cursor()


        inv_update = await self.give_items() #


        for country in inv_update:
            for item, count in country.items():
                if item != 'name' and count != 0:
                    cursor.execute(f"""
                                    UPDATE countries_inventory
                                    SET "{item}" = "{item}" + {float(count)}
                                    WHERE name = "{country['name']}"
                                    """)
        connect.commit()
        connect.close()

        factories = await self.give_factories()
        items = await self.to_items(factories)
        await self.set_upd(items)

    async def send_i_do(self):
        await self.bot.wait_until_ready()
    @update_inventories.before_loop(send_i_do)
    async def pass_module(self):
        pass
        

    async def to_items(self, factories_have: tuple[dict[str, any]]) -> tuple[dict[str, any]]:
        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()


        cursor.execute(f"""
                       SELECT name, produces_key, count
                       FROM factories
                       """)
        # 
        a = cursor.fetchall()
        connect.close()
        result = []

        # Что производит и количество
        tmp = []
        for i in a:
            tmp.append(dict(i)) 
        a = tuple(tmp)

        for j in factories_have:
            b = {}
            b['name'] = j['name']
            for factory in a:
                if factory['produces_key'] != 'Деньги':
                    b[factory['produces_key']] = factory['count'] * j[factory['name']]
            b['Деньги'] = a[-1]['count'] * j[a[-1]['name']] + a[-2]['count'] * j[a[-2]['name']]
            result.append(b)
            
        return tuple(result)


    async def set_upd(self, coutry_items: tuple[dict[str, any]]) -> None:
        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        for items in coutry_items:
            cursor.execute(f"""
                        INSERT OR REPLACE INTO countries_inventory_add ({', '.join(['\"' + i + '\"' for i in items.keys()])})
                        VALUES ({', '.join(['\"' + str(i) + '\"' for i in items.values()])})
                        """)
        connect.commit()
        connect.close()
        return None


    async def give_items(self) -> tuple[dict[str, any], ...]:
        connect = con(DATABASE_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()


        cursor.execute(f"""
                       SELECT *
                       FROM countries_inventory_add
                       """)
        a = cursor.fetchall()


        connect.close()
        result = []
        for i in a:
            result.append(dict(i))
        return tuple(result)
    
    @commands.command(name='collect')
    async def no_collect(self, ctx: commands.Context):
        ctx.reply('У нас нет этой команды! Деньги и армия обновляется автоматически!')


        

async def setup(bot):
    await bot.add_cog(UpdaterCog(bot))