from ..library.modules import hybrid_command, has_permissions, Context, con, deps, Guild

class VipeCommand:
    def __init__(self, guild: Guild):
        self.guild = guild

    @hybrid_command(description='Начинает или заканчивает вайп')
    @has_permissions(administrator=True)
    async def vipe(self, ctx: Context):
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                       SELECT name
                       FROM roles
                       WHERE is_busy IS NOT NULL
                       """)
        result = cursor.fetchall()
        connect.close()

        for country_name in result:
            await deps.Country(country_name[0]).unreg()
        
        connect = con(deps.DATABASE_COUNTRIES_PATH)
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

        deps.game_state['game_started'] = not deps.game_state['game_started']

        if ctx.interaction:
            await ctx.interaction.followup.send('Новый вайп начался!' if deps.game_state['game_started'] else 'Этот вайп закончился!', ephemeral=False)
        else:
            await ctx.send('Новый вайп начался!' if deps.game_state['game_started'] else 'Этот вайп закончился!')