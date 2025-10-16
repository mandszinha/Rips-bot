import discord
from discord.ext import commands
import asyncio
import time
from playwright.async_api import async_playwright, TimeoutError
from config import TOKEN, TIKTOK_USER, ROLE_NAME

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Ajustes de user agent e delays para parecer um navegador real
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

async def check_if_in_olirips_followers(target_username: str, timeout_seconds: int = 60):
    """
    Verifica se target_username (sem @) está na lista de seguidores de @olirips.
    Retorna: True / False / "timeout" / "private" / "error"
    """
    target_username = target_username.lower().lstrip("@")
    olirips = TIKTOK_USER.lstrip("@")

    profile_url = f"https://www.tiktok.com/@{olirips}"
    print(f"[check] Abrindo perfil {profile_url} para procurar {target_username}")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()

        # Set headers to reduce bloqueios automáticos
        await page.set_extra_http_headers({"user-agent": USER_AGENT})
        await page.set_viewport_size({"width": 1280, "height": 800})

        start_time = time.time()
        try:
            # Vai para o perfil do olirips
            await page.goto(profile_url, timeout=20000)
            await page.wait_for_selector("body", timeout=10000)

            html_start = await page.content()
            # detecta se o perfil do alvo está privado / inacessível
            if "This account is private" in html_start or "Essa conta é privada" in html_start:
                return "private"

            # Tenta clicar no elemento "Seguidores" / "Followers"
            # Seletores múltiplos para resistência a variações do layout
            followers_selector_candidates = [
                'a[href$="/followers"]',                       # link direto
                'a:has-text("Followers")',                     # english text
                'a:has-text("Seguidores")',                    # pt-br
                'button:has-text("Followers")',
                'button:has-text("Seguidores")'
            ]
            clicked = False
            for sel in followers_selector_candidates:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        await el.click()
                        clicked = True
                        break
                except Exception:
                    continue

            # Se não encontrou um botão/link, tenta abrir a url direta /followers
            if not clicked:
                followers_url = f"https://www.tiktok.com/@{olirips}/followers"
                await page.goto(followers_url, timeout=20000)
                await page.wait_for_selector("body", timeout=10000)

            # Aguardamos um container que contenha a lista — usamos body como fallback
            await page.wait_for_timeout(800)  # pequeno delay para o JS começar
            elapsed = 0
            prev_height = 0

            # Scroll e busca até timeout_seconds
            while (time.time() - start_time) < timeout_seconds:
                # Pega o HTML atual e procura pelo username
                html = await page.content()
                if target_username in html.lower():
                    return True

                # Scroll down para carregar mais seguidores
                # Executa scroll na página
                try:
                    await page.evaluate(
                        """() => {
                            window.scrollBy(0, window.innerHeight);
                        }"""
                    )
                except Exception:
                    pass

                # aguarda um pouco para permitir load dinâmico
                await page.wait_for_timeout(800)

                # se não houver mudança no conteúdo por alguns ciclos, podemos tentar expandir com mais espera
                elapsed += 1
            # tempo esgotado procurando
            return False

        except TimeoutError:
            print("[check] Timeout ao acessar TikTok.")
            return "timeout"
        except Exception as e:
            print(f"[check] Erro inesperado: {e}")
            return "error"
        finally:
            await browser.close()


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


@bot.command()
async def verificar(ctx):
    """Fluxo interativo:
       1) Pergunta @ do TikTok ao usuário
       2) Verifica se esse @ está entre os seguidores de @olirips
       3) Atribui a role se True
    """
    try:
        await ctx.send("📱 Qual é o seu @ no TikTok? (sem o @, por exemplo: `usuario123`)")
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
        return await ctx.send("Por favor informe um @ válido (ex: `usuario123`).")

    waiting_msg = await ctx.send(f"🔍 Verificando se **@{username}** está entre os seguidores de {TIKTOK_USER}... (pode demorar um pouco)")

    # Chama a verificação com limite máximo de 60 segundos (opção 3)
    result = await check_if_in_olirips_followers(username, timeout_seconds=60)

    # Recupera role e membro
    role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)
    member = ctx.author  # quem pediu a verificação

    # Interpreta resultados
    if result is True:
        try:
            if role and role not in member.roles:
                await member.add_roles(role)
            await waiting_msg.edit(content=f"✅ Você segue {TIKTOK_USER}! Cargo **{ROLE_NAME}** atribuído com sucesso!")
        except Exception as e:
            print(f"[verificar] Erro ao adicionar role: {e}")
            await waiting_msg.edit(content="✅ Você segue, mas ocorreu um erro ao atribuir o cargo. Verifique as permissões do bot.")
    elif result == "private":
        await waiting_msg.edit(content="🔒 O perfil do TikTok está privado ou inacessível. Torne-o público para verificação.")
    elif result == "timeout":
        await waiting_msg.edit(content="⚠️ O TikTok demorou muito para responder. Tente novamente em alguns minutos.")
    elif result == "error":
        await waiting_msg.edit(content="❌ Ocorreu um erro ao verificar o TikTok. Tente novamente mais tarde.")
    else:
        await waiting_msg.edit(content=f"🚫 Você deve seguir {TIKTOK_USER} para receber o cargo **{ROLE_NAME}**.")

# Rodar o bot
bot.run(TOKEN)
