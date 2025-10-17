import discord
from discord.ext import commands
import asyncio
from TikTokApi import TikTokApi
from config import TOKEN, TIKTOK_USER, ROLE_NAME

# --- Intents do Discord ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Evento ready ---
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# --- Função para checar se o usuário segue @olirips ---
def check_if_follows(user_username: str, target_username: str):
    """
    Retorna True se user_username segue target_username
    """
    try:
        with TikTokApi() as api:
            user_following = api.user(username=user_username).following()
            for u in user_following:
                if u.username.lower() == target_username.lower():
                    return True
            return False
    except Exception as e:
        print(f"[TikTokAPI] Erro: {e}")
        return None  # erro

# --- Comando !verificar ---
@bot.command()
async def verificar(ctx):
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
    result = check_if_follows(username, TIKTOK_USER)

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
    elif result is False:
        await waiting_msg.edit(content=f"🚫 Você precisa seguir {TIKTOK_USER} para receber o cargo **{ROLE_NAME}**.")
    else:
        await waiting_msg.edit(content="❌ Ocorreu um erro ao verificar o TikTok. Tente novamente mais tarde.")

# --- Rodar bot ---
bot.run(TOKEN)
