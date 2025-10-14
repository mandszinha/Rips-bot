import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def verificar(ctx):
    await ctx.send("Por favor, envie seu usuário do TikTok (ex: @olirips).")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        tiktok_user = msg.content.strip()
        if tiktok_user.lower() == "@olirips":
            role = discord.utils.get(ctx.guild.roles, name="RIPS")
            if role:
                await ctx.author.add_roles(role)
                await ctx.send(f"✅ Você foi verificado como seguidor do {tiktok_user} e recebeu o cargo **RIPS**!")
            else:
                await ctx.send("❌ Cargo 'RIPS' não encontrado no servidor.")
        else:
            await ctx.send("❌ Nome de usuário inválido ou diferente do TikTok informado.")
    except:
        await ctx.send("⏰ Tempo limite atingido. Tente novamente usando !verificar.")

bot.run(os.getenv("DISCORD_TOKEN"))
