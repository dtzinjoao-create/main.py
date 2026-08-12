import os
import discord
from discord.ext import commands
from discord.ui import Select, View

# --- CONFIGURAÇÕES DO BOT ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID do cargo de suporte puxado das variáveis de ambiente do Railway
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
            discord.SelectOption(
                label="Receber evento",
                description="Clique aqui para receber o seu evento.",
                value="receber_evento",
                emoji="<:emoji_3:1536874334499381278>"
            ),
            discord.SelectOption(
                label="Vaga mediador",
                description="Clique aqui para se candidatar à vaga de mediador.",
                value="vaga_mediador",
                emoji="<:emoji_4:1536877108360515765>"
            ),
            discord.SelectOption(
                label="Divulgação",
                description="Clique aqui para tratar sobre divulgações e parcerias.",
                value="divulgacao",
                emoji="<:emoji_5:1536880689553870948>"
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

        # 1. Responde na hora avisando que está verificando
        await interaction.response.send_message(
            content="**verificando...**",
            ephemeral=True
        )

        if opcao == "opcao_1":
            nome_topico = f"atendimento-{usuario.name}"
            msg_boas_vindas = f"Olá {usuario.mention}, você abriu um atendimento para **Primeira Opção**! Aguarde um suporte."
        
        elif opcao == "reembolso":
            nome_topico = f"reembolso-{usuario.name}"
            msg_boas_vindas = f"Olá {usuario.mention}, você solicitou **REEMBOLSO**. Aguarde um responsável para dar andamento ao seu pedido."

        elif opcao == "receber_evento":
            nome_topico = f"evento-{usuario.name}"
            msg_boas_vindas = f"Olá {usuario.mention}, você abriu um ticket para **Receber evento**. Aguarde a equipe para resgatar sua recompensa!"

        elif opcao == "vaga_mediador":
            nome_topico = f"mediador-{usuario.name}"
            msg_boas_vindas = f"Olá {usuario.mention}, você abriu um chamado referente à **Vaga mediador**. Aguarde um responsável pela equipe!"

        elif opcao == "divulgacao":
            nome_topico = f"divulgacao-{usuario.name}"
            msg_boas_vindas = f"Olá {usuario.mention}, você abriu um ticket sobre **Divulgação**. Aguarde a equipe responsável para tratar do assunto!"

        # 2. Criação do Tópico Privado
        topico = await canal.create_thread(
            name=nome_topico,
            type=discord.ChannelType.private_thread,
            auto_archive_duration=1440
        )

        # 3. Notifica dentro do tópico privado
        await topico.send(
            content=f"{usuario.mention} <@&{ID_CARGO_SUPORTE}>\n\n{msg_boas_vindas}"
        )

        # 4. Atualiza a mensagem confirmando a criação do ticket
        await interaction.edit_original_response(
            content=f"ticket criado com sucesso! {topico.mention}"
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
    
