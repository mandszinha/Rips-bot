@bot.command()
async def verificar(ctx):
    """Pergunta o TikTok do usuário e atribui cargo se segue @olirips"""
    
    # Evita enviar mensagem duplicada
    try:
        await ctx.send("📱 Qual é o seu @ no TikTok? (ex: usuario123)")
    except Exception as e:
        print(f"[verificar] Não consegui enviar pergunta: {e}")
        return

    try:
        msg = await bot.wait_for(
            "message",
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
    except asyncio.TimeoutError:
        return await ctx.send("⏰ Tempo esgotado. Tente novamente com `!verificar`.")

    username = msg.content.replace("@", "").strip()
    if username == "":
        return await ctx.send("Por favor informe um @ válido.")

    waiting_msg = await ctx.send(f"🔍 Verificando se **@{username}** segue {TIKTOK_USER}...")

    # --- Chamada segura da TikTok-API ---
    try:
        from tiktokapipy import TikTokAPI

        api = TikTokAPI()
        olirips_followers = await api.user_followers(TIKTOK_USER.lstrip("@"), limit=1000)
        follower_usernames = [u.username.lower() for u in olirips_followers]

        if username.lower() in follower_usernames:
            role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)
            member = ctx.author
            if role and role not in member.roles:
                await member.add_roles(role)
            await waiting_msg.edit(content=f"✅ Você segue {TIKTOK_USER}! Cargo **{ROLE_NAME}** atribuído!")
        else:
            await waiting_msg.edit(content=f"🚫 Você precisa seguir {TIKTOK_USER} para receber o cargo **{ROLE_NAME}**.")

    except Exception as e:
        print(f"[verificar] Erro TikTok-API: {e}")
        await waiting_msg.edit(content="❌ Ocorreu um erro ao verificar o TikTok. Tente novamente mais tarde.")
