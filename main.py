import discord
from discord.ext import commands
import os
import aiohttp
import asyncio
import random
import string

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def generate_code(length: int = 8):
    part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"RIPS-{part}"

async def fetch_profile_html(session, handle, timeout=15):
    url = f"https://www.tiktok.com/@{handle.lstrip('@')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        async with session.get(url, headers=headers, timeout=timeout) as resp:
            # Alguns perfis podem bloquear; aceitar status 200
            if resp.status == 200:
                text = await resp.text()
                return text
            else:
                return None
    except Exception as e:
        return None

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def verificar(ctx):
    """Verificação via código temporário na bio do TikTok."""
    author = ctx.author

    await ctx.send("Por favor, envie seu usuário do TikTok (ex: @findthatpikachu).")

    def check_msg(m):
        return m.author == author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check_msg, timeout=60)
        tiktok_handle = msg.content.strip().lstrip("@")
        if not tiktok_handle:
            await ctx.send("Usuário inválido. Tente novamente com algo como @usuario.")
            return

        code = generate_code(6)
        await ctx.send(
            f"Para provar que você segue @olirips, por favor **adicione temporariamente** o código abaixo na sua bio do TikTok:\n\n"
            f"`{code}`\n\n"
            "Depois de adicionar, responda aqui `pronto`. Você tem 3 minutos."
        )

        try:
            confirm = await bot.wait_for("message", check=lambda m: m.author == author and m.channel == ctx.channel and m.content.lower() == "pronto", timeout=180)
        except asyncio.TimeoutError:
            await ctx.send("⏰ Tempo esgotado. Tente novamente com `!verificar` quando estiver pronto.")
            return

        await ctx.send("Verificando bio do TikTok... aguarde alguns segundos.")

        async with aiohttp.ClientSession() as session:
            html = await fetch_profile_html(session, tiktok_handle)
            if html is None:
                await ctx.send("❌ Não consegui acessar o perfil do TikTok. O perfil pode estar privado, bloqueado, ou o TikTok pode estar bloqueando requisições automatizadas. Tente novamente mais tarde.")
                return

            # Procura código no HTML
            if code in html:
                role = discord.utils.get(ctx.guild.roles, name="RIPS")
                if role is None:
                    await ctx.send("❌ Cargo 'RIPS' não encontrado no servidor. Peça ao administrador criar o cargo.")
                    return

                # Verifique se o bot pode adicionar roles: cargo do bot deve estar acima do cargo "RIPS".
                try:
                    await ctx.author.add_roles(role)
                    await ctx.send(f"✅ Verificação concluída! Você recebeu o cargo **{role.name}**.")
                except discord.Forbidden:
                    await ctx.send("❌ Não tenho permissão para adicionar esse cargo. Coloque o cargo do bot acima do cargo RIPS na hierarquia.")
                except Exception as e:
                    await ctx.send(f"❌ Erro ao adicionar cargo: {e}")
            else:
                await ctx.send("❌ Código não encontrado na bio. Verifique se você colocou exatamente o código e se salvou a bio. Tente novamente.")

    except asyncio.TimeoutError:
        await ctx.send("⏰ Tempo limite. Use `!verificar` para recomeçar.")
