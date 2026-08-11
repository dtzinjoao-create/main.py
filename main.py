import os
import discord
from discord.ext import commands
from discord.ui import Select, View

# --- CONFIGURAÇÕES DO BOT ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Puxa o ID do cargo das variáveis do Railway (ou usa o ID direto se preferir)
ID_CARGO_SUPORTE = int(os.getenv("ID_CARGO_SUPORTE", 123456789012345678))


# --- DEFINIÇÃO DO MENU (SELECT) ---
class MenuAjudaSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Primeira Opção",
                description="Clique aqui para ver a primeira opção.",
                value="opcao_1",
                emoji="<:emoji_2:1536869754944487486>"
            ),
            discord.SelectOption(
                label="REEMBOLSO",
                description="Clique aqui para caso um reembolso.",
                value="reembolso",
                emoji="<:emoji_3:1536867013979279360>"
            ),
        ]
        
        super().__init__(
            placeholder="Selecione uma opção...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="menu_atendimento_select"
        )

    async def callback(self, interaction: discord.Interaction):
        opcao = self.values[0]
        usuario = interaction.user
        canal = interaction.channel

        await interaction.response.defer(ephemeral=True)

        if opcao == "opcao_1":
            nome_topico = f"atendimento-{usuario.name}"
            msg_boas_vindas = f"Olá {usuario.mention}, você abriu um atendimento para **Primeira Opção**! Aguarde um suporte."
        
        elif opcao == "reembolso":
            nome_topico = f"reembolso-{usuario.name}"
            msg_boas_vindas = f"Olá {usuario.mention}, você solicitou **REEMBOLSO**. Aguarde um responsável para dar andamento ao seu pedido."

        # Criação do Tópico Privado
        topico = await canal.create_thread(
            name=nome_topico,
            type=discord.ChannelType.private_thread,
            auto_archive_duration=1440
        )

        # Notifica e adiciona silenciosamente os envolvidos
        await topico.send(
            content=f"{usuario.mention} <@&{ID_CARGO_SUPORTE}>\n\n{msg_boas_vindas}"
        )

        await interaction.followup.send(
            content=f"Seu atendimento foi aberto com sucesso em: {topico.mention}",
            ephemeral=True
        )


# --- VIEW DO MENU ---
class MenuAjudaView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MenuAjudaSelect())


# --- EVENTOS DO BOT ---
@bot.event
async def on_ready():
    bot.add_view(MenuAjudaView())
    print(f"Bot online como {bot.user.name}!")


# --- COMANDO PARA ENVIAR O PAINEL ---
@bot.command(name="painel")
@commands.has_permissions(administrator=True)
async def enviar_painel(ctx):
    embed = discord.Embed(
        title="Central de Atendimento",
        description="Escolha uma das opções abaixo para abrir um chamado privado:",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Selecione a opção no menu abaixo.")
    
    await ctx.send(embed=embed, view=MenuAjudaView())


# --- INICIALIZAÇÃO VIA VARIÁVEL DE AMBIENTE (RAILWAY) ---
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
