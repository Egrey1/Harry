from ..library.modules import  (hybrid_command, Context, 
                                File, BytesIO, requests_get, wrap, 
                                Image, ImageDraw, ImageFont, ImageOps)

class Quote:
    def __init__(self):
        pass


    def create_quote(self, text, author_name, avatar_bytes):
        W, H = 1000, 500
        img = Image.new('RGB', (W, H), color=(0, 0, 0))
        

        avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
        avatar = ImageOps.fit(avatar, (500, 500))
        

        mask = Image.new('L', (500, 500), 0)
        mask_draw = ImageDraw.Draw(mask)
        for x in range(500):
            opacity = int(255 * (1 - (x / 450))) 
            mask_draw.line((x, 0, x, 500), fill=max(0, opacity))
        
        img.paste(avatar, (0, 0), mask)
        draw = ImageDraw.Draw(img)
        

        try:
            font_main = ImageFont.truetype("arial.ttf", 36)
            font_author = ImageFont.truetype("arial.ttf", 23)
        except:
            font_main = ImageFont.load_default()
            font_author = ImageFont.load_default()

        lines = wrap(text, width=25)
        y_text = 150 
        for line in lines:
            draw.text((520, y_text), line, font=font_main, fill="white")
            y_text += 50 

        draw.text((520, y_text + 20), f"- {author_name}", font=font_author, fill=(180, 180, 180))
        draw.text((750, 460), "SkyTechDev inc", font=font_author, fill=(50, 50, 50))

        return img

    @hybrid_command(name='quote', description='Создать красивую цитату из сообщения')
    async def quote(self, ctx: Context):
        if not ctx.message.reference:
            return await ctx.reply("Ответьте на сообщение, которое хотите превратить в цитату!", ephemeral=True)
        
        orig_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        
        content = orig_msg.content if orig_msg.content else "[Изображение/Вложение]"


        author_name = orig_msg.author.global_name or orig_msg.author.name

        avatar_url = orig_msg.author.display_avatar.with_format("png").url
        avatar_bytes = requests_get(avatar_url).content

        final_img = self.create_quote(content, author_name, avatar_bytes)

        with BytesIO() as out:
            final_img.save(out, format="PNG")
            out.seek(0)
            await ctx.send(file=File(fp=out, filename="quote.png"))
