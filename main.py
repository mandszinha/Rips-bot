import discord
from discord.ext import commands
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from config import TOKEN, TIKTOK_USER, ROLE_NAME

# Configuração dos intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Função que verifica se o usuário segue o perfil desejado
async def check_following(user_tiktok):
    url = f"https://www.tiktok.com/@{user_tiktok}/following"
    print(f"Verificando URL: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=20000)
            await page.wait_for_selector('body', timeout=10000)
            html = await page.content()

            if "This account is private" in html or "Essa conta é privada" in html:
                return "private"

            # Verifica se o perfil seguido aparece na lista
            return TIKTOK_USER.lower() in html.lower()

        except TimeoutError:
            print("⏰ Timeout ao carregar a página do TikTok.")
            return "timeout"
        except Exception as e:
            print(f"❌ Erro ao verificar TikTok: {e}")
            return "error"
        finally:
            await browser.close()

# Evento quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# Comando !verificar
@bot.command()
async def verificar(ctx):
    await ctx.send("📱 Qual é o seu @ no TikTok? (sem o @, por exemplo: `usuario123`)")

    try:
        msg = await bot.wait_for(
            "message",
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
    except asyncio.TimeoutError:
        return await ctx.send("⏰ Tempo esgotado. Tente novamente com `!verificar`.")

    username = msg.content.replace("@", "").strip().lower()
    await ctx.send(f"🔍 Verificando se **@{username}** segue {TIKTOK_USER}...")

    follows = await check_following(username)
    role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)

    if follows is True:
        if role not in ctx.author.roles:
            await ctx.author.add_roles(role)
        await ctx.send(f"✅ Você segue {TIKTOK_USER}! Cargo **{ROLE_NAME}** atribuído com sucesso!")
    elif follows == "private":
        await ctx.send("🔒 Seu perfil do TikTok é privado. Torne-o público para verificação.")
    elif follows == "timeout":
        await ctx.send("⚠️ O TikTok demorou muito para responder. Tente novamente em alguns minutos.")
    elif follows == "error":
        await ctx.send("❌ Ocorreu um erro ao verificar o TikTok. Tente novamente mais tarde.")
    else:
        await ctx.send(f"🚫 Você deve seguir {TIKTOK_USER} para receber o cargo **{ROLE_NAME}**.")

bot.run(TOKEN)
