from .modules import con, ROLE_PICKER_PATH, DATABASE_PATH, Row, Interaction, roles_id

async def give_all_countries() -> tuple:
    connect = con(ROLE_PICKER_PATH)
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT name
                    FROM roles
                    """)
    result = tuple([row[0] for row in cursor.fetchall()])  
    connect.close()
    return result

async def give_all_no_surrend_countries() -> tuple:
    connect = con(ROLE_PICKER_PATH)
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT name
                    FROM roles
                    WHERE surrender IS NULL
                    """)
    result = tuple([row[0] for row in cursor.fetchall()])  
    connect.close()
    return result

async def give_all_surrend_countries() -> tuple:
    connect = con(ROLE_PICKER_PATH)
    cursor = connect.cursor()
    cursor.execute(f"""
                    SELECT name
                    FROM roles
                    WHERE surrender IS NOT NULL
                    """)
    result = tuple([row[0] for row in cursor.fetchall()])  
    connect.close()
    return result

async def give_all_factories() -> tuple:
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute("""
                SELECT name, cost, `desc`
                FROM factories
                """)
    a = cursor.fetchall()
    connect.close()
    result = []

    for i in a:
        result.append(dict(i))
    
    return tuple(result)

# It should work, I didn't check it.
async def give_all_proops() -> tuple:
    connect = con(DATABASE_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute("""
                SELECT *
                FROM countries_inventory
                """)
    a = cursor.fetchone()
    connect.close()
    result = []

    a = dict(a)
    result = (j for j in a.keys() if j != 'name')
    
    return result


async def unreg_function(country: str, interaction: Interaction) -> None:

        if not country:
            return None
        user = interaction.user
        for id in roles_id.values():
            try:
                role = interaction.guild.get_role(id) 
                await user.remove_roles(role) 
            except:
                continue
        # unreg = interaction.guild.get_role(1344519330091503628)
        # await user.add_roles(unreg)  
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
