import discord
from discord.ext import commands
import asyncio
import random
import string
import aiohttp
from playwright.async_api import async_playwright
from config import TOKEN, TIKTOK_USER, ROLE_NAME

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def check_following(username):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(f"https://www.tiktok.com/@{username}")
            # Verifica se existe botão "Seguir" ou algo que indique que não segue @olirips
            # Aqui você pode adaptar conforme a estrutura do TikTok
            content = await page.content()
            follows = TIKTOK_USER.lower() in content.lower()
            return follows
        except Exception as e:
            print(f"Erro ao verificar TikTok: {e}")
            return False
        finally:
            await browser.close()

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def verificar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"Verificando {member.name} no TikTok...")

    follows = await check_following(member.name)  # Aqui você pode ajustar para pegar username real do TikTok
    role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)

    if follows:
        if role not in member.roles:
            await member.add_roles(role)
        await ctx.send(f"{member.name} está seguindo {TIKTOK_USER}! Role '{ROLE_NAME}' atribuída ✅")
    else:
        await ctx.send(f"{member.name} NÃO está seguindo {TIKTOK_USER} ❌")

bot.run(TOKEN)
