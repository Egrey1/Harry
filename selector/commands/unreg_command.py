from ..library.modules import deps, Context, hybrid_command, Interaction, con, datetime


class UnregCommand:
    def __init__(self):
        pass

    @hybrid_command(description='Снимает с вас регистрацию со страны')
    async def unreg(self, ctx: Context) -> None:
        country = deps.Country(ctx.author.mention)
        await ctx.interaction.response.defer(ephemeral=True)
        
        if country.busy is None:
            try:
                await ctx.send('Вы и так не страна!', ephemeral= True) # not country trying unreg
            except:
                await ctx.channel.send(f'{ctx.author.mention} Вы и так не страна!')
            return None
        
        await country.unreg()

        # Обновляем last_register для пользователя
        new_value = datetime.datetime.now().isoformat()
        connect = con(deps.DATABASE_CONFIG_PATH)
        cursor = connect.cursor()
        
        # Проверяем, есть ли уже запись для этого пользователя
        cursor.execute("""
                        SELECT id
                        FROM users
                        WHERE id = ?
        """, (ctx.author.id,))
        result = cursor.fetchone()
        
        if result:
            # UPDATE если запись существует
            cursor.execute("""
                            UPDATE users
                            SET last_register = ?
                            WHERE id = ?
            """, (new_value, ctx.author.id))
        else:
            # INSERT если записи нет
            cursor.execute("""
                            INSERT INTO users (id, last_register)
                            VALUES (?, ?)
            """, (ctx.author.id, new_value))
        
        connect.commit()
        connect.close()

        try:
            await ctx.send('Вы больше не страна!', ephemeral= True)
        except:
            await ctx.channel.send(f'{ctx.author.mention} Вы больше не страна!')
