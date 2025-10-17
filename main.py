import discord
from discord.ext import commands
import asyncio
import time
from playwright.async_api import async_playwright, TimeoutError
from config import TOKEN, TIKTOK_USER, ROLE_NAME

# --- Intents do Discord ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- User agent para parecer navegador real ---
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# --- Função para verificar seguidores ---
async def check_if_in_olirips_followers(target_username: str, timeout_seconds: int = 60):
    target_username = target_username.lower().lstrip("@")
    olirips = TIKTOK_USER.lstrip("@")

    profile_url = f"https://www.tiktok.com/@{olirips}"
    print(f"[check] Abrindo perfil {profile_url} para procurar {target_username}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,             # headless obrigatório no Replit
            args=["--no-sandbox"]      # evita travamentos
        )
        page = await browser.new_page()
        await page.set_extra_http_headers({"user-agent": USER_AGENT})
        await page.set_viewport_size({"width": 1280, "height": 800})

        start_time = time.time()
        try:
            await page.goto(profile_url, timeout=20000)
            await page.wait_for_selector("body", timeout=10000)

            html_start = await page.content()
            if "This account is private" in html_start or "Essa conta é privada" in html_start:
                return "private"

            # Scroll infinito para tentar achar o username
            while (time.time() - start_time) < timeout_seconds:
                html = await page.content()
                if target_username in html.lower():
                    return True
                await page.evaluate("() => { window.scrollBy(0, window.innerHeight); }")
                await page.wait_for_timeout(800)

            return False

        except TimeoutError:
            print("[check] Timeout ao acessar TikTok.")
            return "timeout"
        except Exception as e:
            print(f"[check] Erro inesperado: {e}")
            return "error"
        finally:
            await browser.close()


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
    result = await check_if_in_olirips_followers(username, timeout_seconds=60)

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
    elif result == "private":
        await waiting_msg.edit(content="🔒 Perfil privado. Torne-o público para verificação.")
    elif result == "timeout":
        await waiting_msg.edit(content="⚠️ TikTok demorou muito para responder. Tente novamente mais tarde.")
    elif result == "error":
        await waiting_msg.edit(content="❌ Ocorreu um erro ao verificar o TikTok. Tente novamente mais tarde.")
    else:
        await waiting_msg.edit(content=f"🚫 Você precisa seguir {TIKTOK_USER} para receber o cargo **{ROLE_NAME}**.")


# --- Rodar bot ---
bot.run(TOKEN)
