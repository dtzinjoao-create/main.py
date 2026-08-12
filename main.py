import os
import discord
from discord.ext import commands
from discord.ui import Select, View, Button

# --- CONFIGURAÇÕES DO BOT ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID do cargo de suporte puxado das variáveis de ambiente do Railway
ID_CARGO_SUPORTE = int(os.getenv("ID_CARGO_SUPORTE", 123456789012345678))

# URL da imagem do logotipo/thumbnail do ticket
URL_THUMBNAIL_TICKET = "https://i.imgur.com/8N4aQ8L.png"


# --- VIEW COM OS BOTÕES DO TICKET ---
class PainelTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistente

    @discord.ui.button(
        label="Assumir",
        style=discord.ButtonStyle.success,
        emoji="<:emoji_10:1536910081730412674>",  # Emoji atualizado
        custom_id="btn_assumir_ticket"
    )
    async def assumir_callback(self, interaction: discord.Interaction, button: Button):
        cargo_suporte = interaction.guild.get_role(ID_CARGO_SUPORTE)
        if cargo_suporte not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "Apenas membros da equipe podem assumir este ticket!",
                ephemeral=True
            )

        embed_assumido = discord.Embed(
            description=f"📌 O suporte {interaction.user.mention} assumiu este atendimento!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed_assumido)

    @discord.ui.button(
        label="Finalizar",
        style=discord.ButtonStyle.danger,
        emoji="<:emoji_9:1536910049870610624>",  # Emoji atualizado
        custom_id="btn_finalizar_ticket"
    )
    async def finalizar_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "🔒 **O ticket será fechado e arquivado em 5 segundos...**"
        )
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.edit(archived=True, locked=True)

    @discord.ui.button(
        label="Painel Staff",
        style=discord.ButtonStyle.primary,
        emoji="<:emoji_2:1536869754944487486>",  # Emoji atualizado
        custom_id="btn_painel_staff"
    )
    async def painel_staff_callback(self, interaction: discord.Interaction, button: Button):
        cargo_suporte = interaction.guild.get_role(ID_CARGO_SUPORTE)
        if cargo_suporte not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "Você não tem permissão para acessar o Painel Staff.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "🛠️ **Painel Staff:** Utilize os comandos administrativos de gerenciamento de chamados aqui.",
            ephemeral=True
        )


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

        await interaction.response.send_message(
            content="**verificando...**",
            ephemeral=True
        )

        if opcao == "opcao_1":
            nome_topico = f"atendimento-{usuario.name}"
        elif opcao == "reembolso":
            nome_topico = f"reembolso-{usuario.name}"
        elif opcao == "receber_evento":
            nome_topico = f"evento-{usuario.name}"
        elif opcao == "vaga_mediador":
            nome_topico = f"mediador-{usuario.name}"
        elif opcao == "divulgacao":
            nome_topico = f"divulgacao-{usuario.name}"

        # 1. Criação do Tópico Privado
        topico = await canal.create_thread(
            name=nome_topico,
            type=discord.ChannelType.private_thread,
            auto_archive_duration=1440
        )

        # 2. Montagem do Embed do Ticket
        embed_ticket = discord.Embed(
            title="Ticket de Suporte",
            description=(
                "Seja bem-vindo(a) ao painel de controle deste ticket.\n"
                "Dependendo do horário em que este ticket foi aberto, "
                "os atendimentos podem demorar um pouquinho.\n\n"
                "*Em breve os atendentes irão lhe atender, peço que tenha paciência.*"
            ),
            color=discord.Color.from_rgb(255, 20, 147)
        )
        embed_ticket.set_thumbnail(url=URL_THUMBNAIL_TICKET)

        # 3. Envia as menções + Embed + Botões Personalizados no tópico privado
        await topico.send(
            content=f"{usuario.mention} <@&{ID_CARGO_SUPORTE}>",
            embed=embed_ticket,
            view=PainelTicketView()
        )

        # 4. Atualiza a mensagem confirmando a criação
        await interaction.edit_original_response(
            content=f"ticket criado com sucesso! {topico.mention}"
        )


# --- VIEW DO MENU INICIAL ---
class MenuAjudaView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MenuAjudaSelect())


# --- EVENTOS DO BOT ---
@bot.event
async def on_ready():
    bot.add_view(MenuAjudaView())
    bot.add_view(PainelTicketView())
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

if not TOKEN:
    raise ValueError("ERRO CRÍTICO: A variável 'DISCORD_TOKEN' não foi configurada no Railway!")

bot.run(TOKEN)
            
