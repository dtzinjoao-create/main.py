import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- MENU SUSPENSO ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Suporte", 
                description="Clique aqui caso precise de um suporte.", 
                emoji="<:emoji_1:1536798022384754789>",
                value="suporte"
            )
        ]
        
        super().__init__(
            placeholder="Clique aqui para escolher uma opção",
            min_values=1, 
            max_values=1, 
            options=options,
            custom_id="ticket_select_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        # Aqui é onde vai responder quando a pessoa clicar na opção Suporte
        if self.values[0] == "suporte":
            await interaction.response.send_message(
                "Você selecionou a opção de **Suporte**! Em breve o canal do seu ticket será criado.", 
                ephemeral=True
            )

# --- CONTÊINER PERSISTENTE ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- COMANDO DO PAINEL ---
@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    embed = discord.Embed(
        title="Painel de Atendimento",
        description="Caso precise de algum suporte ou tenha alguma dúvida basta abrir um ticket abaixo. "
                    "Selecione a opção do ticket de acordo com a sua necessidade.",
        color=discord.Color.from_rgb(255, 20, 147)
    )

    await ctx.send(embed=embed, view=TicketView())

@bot.event
async def on_ready():
    bot.add_view(TicketView())
    print(f'Bot conectado com sucesso como {bot.user.name}')

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRO: A variável 'DISCORD_TOKEN' não foi encontrada.")
