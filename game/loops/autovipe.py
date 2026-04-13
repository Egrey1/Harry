from ..library import loop, deps, con, logging

class Autovipe:
    @loop(hours= deps.autovipe)
    async def autovipe(self):
        logging.info('Происходит автовайп')

        deps.game_state['game_started'] = not deps.game_state['game_started']
        if deps.game_state['game_started']:
            return

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

        cursor.execute("""
                        DELETE FROM market
                        """)
        connect.commit()
        connect.close()

        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       DELETE FROM roles
                       """)
        cursor.execute("""
                       INSERT INTO roles
                       SELECT *
                       FROM roles_default
                       """)
        connect.commit()
        connect.close()

        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       DELETE FROM countries
                       """)
        cursor.execute("""
                       INSERT INTO countries
                       SELECT *
                       FROM countries_default
                       """)
        connect.commit()
        connect.close()

        connect = con(deps.DATABASE_CONFIG_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       UPDATE users
                       SET last_register = NULL
                       """)
        connect.commit()
        connect.close()

        await deps.rp_channels.del_event()
        await deps.rp_channels.del_news()
        await deps.rp_channels.del_war()

        logging.info('Создаем потоки...')
        for country in await deps.Country.all():
            await country.create_news_thread()
        logging.info('Потоки созданы')

        channel = deps.guild.get_channel(deps.CHANNEL_FOR_UPDATE_ID)
        await channel.edit(name='📅┃1/12 1933 год')
