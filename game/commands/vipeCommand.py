from ..library.modules import hybrid_command, has_permissions, Context, con, deps, Guild

from ..library.functions import unreg_function

class VipeCommand:
    def __init__(self, guild: Guild):
        self.guild = guild

    @hybrid_command(description='Начинает или заканчивает вайп')
    @has_permissions(administrator=True)
    async def vipe(self, ctx: Context):
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

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
            await unreg_function(self.guild.get_member(int(member[0][2:-1])), self.guild)
        
        connect = con(DATABASE_COUNTRIES_PATH)
        cursor = connect.cursor()

        cursor.execute(f"DELETE FROM country_factories")
        cursor.execute("""
                       INSERT INTO country_factories
                       SELECT *
                       FROM country_factories_default
                       """)
        connect.commit()

        cursor.execute("DELETE FROM countries_inventory")
        cursor.execute("""
                       INSERT INTO countries_inventory
                       SELECT *
                       FROM countries_inventory_default
                       """)
        connect.commit()
        connect.close()

        game_state['game_started'] = not game_state['game_started']

        if ctx.interaction:
            await ctx.interaction.followup.send('Новый вайп начался!' if game_state['game_started'] else 'Этот вайп закончился!', ephemeral=False)
        else:
            await ctx.send('Новый вайп начался!' if game_state['game_started'] else 'Этот вайп закончился!')