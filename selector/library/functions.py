from selector.library.modules import con, deps, Row, datetime, Member

def can_register(member: Member) -> bool:
    connect = con(deps.DATABASE_CONFIG_PATH)
    cursor = connect.cursor()
    cursor.execute("""
                    SELECT last_register
                    FROM users
                    WHERE id = ?
    """, (member.id,))
    result = cursor.fetchone()
    current_time = datetime.datetime.now()
    
    if not result or not result[0]:
        if not result:
            cursor.execute("""
                        INSERT INTO users (id, last_register)
                        VALUES (?, ?)
            """, (member.id, current_time.isoformat()))
        else:
            cursor.execute("""
                            UPDATE users
                            SET last_register = ?
                            WHERE id = ?
            """, (current_time.isoformat(), member.id))
        connect.commit()
        connect.close()
        return True
    
    connect.close()
    result = datetime.datetime.fromisoformat(result[0])
    return (current_time - result).days >= deps.register_cooldown

# Возвращает словарь где говорит какие роли нужно ставить
async def give_roles(name: str) -> dict:

    connect = con(deps.DATABASE_ROLE_PICKER_PATH)
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
async def give_all_countries() -> tuple:
    connect = con(deps.DATABASE_ROLE_PICKER_PATH)
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT name
                    FROM roles
                    WHERE is_busy IS NULL and surrender IS NULL
                    """)
    result = tuple([row[0] for row in cursor.fetchall()])  
    connect.close()
    return result

# Заносим пользователя в страну как занятого
async def set_is_busy(mention: str, country_name: str | None = None):
        connect = con(deps.DATABASE_ROLE_PICKER_PATH)
        cursor = connect.cursor()
        if country_name:
            cursor.execute(f"""
                        UPDATE roles
                        SET is_busy = '{mention}'
                        WHERE name = '{country_name}'
                        """) 
        else:
             cursor.execute(f"""
                        UPDATE roles
                        SET is_busy = null
                        WHERE is_busy = '{mention}'
                        """)
        connect.commit()
        connect.close()