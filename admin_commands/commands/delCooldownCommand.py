from ..library import hybrid_command, has_permissions, Context, con, deps, Member, describe

class DelCooldownCommand1:
    @hybrid_command(name= 'del_cooldown', description='Удалить кулдаун на регистрацию для страны')
    @has_permissions(administrator= True)
    @describe(member= 'Какому человеку снять кулдаун')
    async def del_cooldown(self, ctx: Context, member: Member):
        connect = con(deps.DATABASE_CONFIG_PATH)
        cursor = connect.cursor()
        cursor.execute("""
                        UPDATE users
                        SET last_register = NULL
                        WHERE id = ?
                        """, (member.id,))
        
        connect.commit()
        connect.close()
        await ctx.reply('Кулдаун удалён', ephemeral= True)