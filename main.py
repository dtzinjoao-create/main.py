import discord
from discord.ext import commands
import os

# --- CONFIGURAÇÃO INICIAL DO BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- MENU SUSPENSO (SELECT MENU) ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        # O Discord exige no mínimo 1 opção no Select. 
        # Esta opção você poderá editar/substituir depois pelas suas categorias!
        options = [
            discord.SelectOption(
                label="Selecione uma opção...", 
                description="Clique aqui para ver o menu.", 
                value="opcao_padrao"
            )
        ]
        
        super().__init__(
            placeholder="Clique aqui para escolher uma opção", # TEXTO EXATO DA IMAGEM
            min_values=1, 
            max_values=1, 
            options=options
        )

    # Ação que executa ao clicar no menu
    async def callback(self, interaction: discord.Interaction):
        # Apenas avisa ao usuário por enquanto (já que você adicionará as opções depois)
        await interaction.response.send_message(
            "Você selecionou a opção do menu! Adicione a lógica do seu ticket aqui depois.", 
            ephemeral=True
        )

# --- CONTÊINER (VIEW) ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # timeout=None mantém o painel ativo permanentemente no Railway
        self.add_item(TicketSelect())

# --- COMANDO PARA ENVIAR O PAINEL ---
@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    # Embed idêntico ao da foto
    embed = discord.Embed(
        title="Painel de Atendimento",
        description="Caso precise de algum suporte ou tenha alguma dúvida basta abrir um ticket abaixo. "
                    "Selecione a opção do ticket de acordo com a sua necessidade.",
        color=discord.Color.from_rgb(255, 20, 147) # Borda rosa
    )
    
    # Se quiser colocar o logo/jaguar do canto superior direito, cole o link direto aqui:
    # embed.set_thumbnail(url="SUA_URL_DA_IMAGEM_AQUI")

    await ctx.send(embed=embed, view=TicketView())

@bot.event
async def on_ready():
    bot.add_view(TicketView())
    print(f'Bot conectado com sucesso como {bot.user.name}')

# --- INICIALIZAÇÃO SEGURA NO RAILWAY ---
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRO: A variável 'DISCORD_TOKEN' não foi encontrada nas variáveis do Railway.")
  
