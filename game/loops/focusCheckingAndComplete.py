from ..library import deps, loop, con, logging

class FocusesLoop():
    @loop(hours=deps.SPEED)
    async def focus_loop(self):
        logging.info('Проверка фокусов и их завершение')

        if not deps.game_state['game_started']:
            return
        
        connect = con(deps.DATABASE_FOCUS_PATH)
        cursor = connect.cursor()
        
        cursor.execute("""
                        SELECT name
                        FROM countries
                        """)
        fetches = cursor.fetchall()
        
        for fetch in fetches:
            country = deps.Country(fetch[0])
            if country.doing_focus is None:
                continue
            
            if not country.doing_focus.req_news and country.doing_focus.requirements_complete():
                country.doing_focus.mark_as_completed(connect=connect)
            
            if country.doing_focus.is_completed:
                await country.doing_focus.complete_focus()
                
                cursor.execute("""
                                UPDATE countries
                                SET doing = ?, completed = ?, current = ?
                                WHERE name = ?
                                """, (None, None, country.doing_focus.name, country.name))
        connect.commit()
        connect.close()
            
            