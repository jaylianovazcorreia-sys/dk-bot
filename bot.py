import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.environ.get("TOKEN")
NOME_ORG = "DK E-SPORTS"
COR_EMBED = 0x00ff88

SLOTS = {"1x1":2,"2x2":4,"3x3":6,"4x4":8}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
filas = {modo: [] for modo in SLOTS}

def build_embed(modo):
    fila = filas[modo]
    j = "\n".join(f"<@{u}>" for u in fila) if fila else "_Nenhum_"
    e = discord.Embed(title=f"{modo} | {NOME_ORG}", color=COR_EMBED)
    e.add_field(name="Modo", value=f"{modo} GRÁTIS", inline=True)
    e.add_field(name="Valor", value="0,00", inline=True)
    e.add_field(name=f"Jogadores ({len(fila)}/{SLOTS[modo]})", value=j, inline=False)
    return e

class FilaView(discord.ui.View):
    def __init__(self, modo):
        super().__init__(timeout=None)
        self.modo = modo
        b1 = discord.ui.Button(label="Entrar na Fila", style=discord.ButtonStyle.success, custom_id=f"entrar_{modo}")
        b2 = discord.ui.Button(label="Sair da Fila", style=discord.ButtonStyle.danger, custom_id=f"sair_{modo}")
        b1.callback = self.entrar
        b2.callback = self.sair
        self.add_item(b1)
        self.add_item(b2)

    async def entrar(self, i):
        uid = i.user.id
        fila = filas[self.modo]
        if uid in fila:
            await i.response.send_message("Já está na fila!", ephemeral=True); return
        fila.append(uid)
        await i.response.edit_message(embed=build_embed(self.modo), view=self)
        if len(fila) >= SLOTS[self.modo]:
            m = " ".join(f"<@{u}>" for u in fila)
            filas[self.modo].clear()
            await i.followup.send(f"🚀 {self.modo} completo! {m}")
            await i.edit_original_response(embed=build_embed(self.modo), view=self)

    async def sair(self, i):
        uid = i.user.id
        fila = filas[self.modo]
        if uid not in fila:
            await i.response.send_message("Não está na fila.", ephemeral=True); return
        fila.remove(uid)
        await i.response.edit_message(embed=build_embed(self.modo), view=self)

@bot.tree.command(name="filas", description="Abre os painéis de fila")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_filas(interaction):
    await interaction.response.send_message("Painéis criados!", ephemeral=True)
    for modo in SLOTS:
        await interaction.channel.send(embed=build_embed(modo), view=FilaView(modo))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot online: {bot.user}")

bot.run(TOKEN)
