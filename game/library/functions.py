from .modules import Member, roles_id, con, Guild
from .modules import DATABASE_ROLE_PICKER as DATABASE_PATH

async def unreg_function(member: Member, guild: Guild):
    for id in roles_id.values():
        try:
            role = guild.get_role(id) 
            await member.remove_roles(role) 
        except:
            continue
    
    unreg = guild.get_role(1344519330091503628)
    await member.add_roles(unreg)  
    try:
        await member.edit(nick='') 
    except:
        pass
    
    connect = con(DATABASE_PATH)
    cursor = connect.cursor()

    cursor.execute(f"""
                    UPDATE roles
                    SET is_busy = null
                    WHERE is_busy = '{member.mention}'
                    """)
    connect.commit()

    connect.close()