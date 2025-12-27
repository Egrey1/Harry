from .modules import Member, deps, con, Guild

async def unreg_function(member: Member, guild: Guild):
    for id in deps.RP_ROLES.values():
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
    
    connect = con(deps.DATABASE_ROLE_PICKER_PATH)
    cursor = connect.cursor()

    cursor.execute(f"""
                    UPDATE roles
                    SET is_busy = null
                    WHERE is_busy = '{member.mention}'
                    """)
    connect.commit()

    connect.close()