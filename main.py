import discord
from discord.ext import commands
import asyncio
from tiktokapipy import TikTokAPI  # Biblioteca TikTok-API
from config import TOKEN, TIKTOK_USER, ROLE_NAME

# --- Intents do Discord ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Função para verificar se o usuário segue @olirips ---
async def check_if_in_olirips_followers(target_username: str):
    target_username = target_username.lstrip("@").lower()
    olirips = TIKTOK_USER.lstrip("@").lower()

    try:
        api = TikTokAPI()  # Cria a instância da API
        # Pega a lista de seguidores de olirips (público)
        followers = await api.user_followers(olirips, limit=1000)  # ajusta limit se necessário
        follower_usernames = [u.username.lower() for u in followers]

        if target_username in follower_usernames:
            return True
        else:
            return False

    except Exception as e:
        print(f"[check] Erro TikTokAPI: {e}")
        return "error"


# --- Evento ready ---
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


# --- Comando !verificar ---
@bot.command()
async def verificar(ctx):
    """Pergunta o TikTok do usuário e atribui cargo se segue @olirips"""
    await ctx.send("📱 Qual é o seu @ no TikTok? (ex: `usuario123`)")

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

    # Checa seguidores
    result = await check_if_in_olirips_followers(username)

    role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)
    member = ctx.author

    if result is True:
        try:
            if role and role not in member.roles:
                await member.add_roles(role)
            await waiting_msg.edit(content=f"✅ Você segue {TIKTOK_USER}! Cargo **{ROLE_NAME}** atribuído!")
        except Exception as e:
            print(f"[verificar] Erro ao adicionar role: {e}")
            await waiting_msg.edit(content="✅ Você segue, mas não foi possível atribuir o cargo.")
    elif result == "error":
        await waiting_msg.edit(content="❌ Ocorreu um erro ao verificar o TikTok. Tente novamente mais tarde.")
    else:
        await waiting_msg.edit(content=f"🚫 Você precisa seguir {TIKTOK_USER} para receber o cargo **{ROLE_NAME}**.")


# --- Rodar bot ---
bot.run(TOKEN)
