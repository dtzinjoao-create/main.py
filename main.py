import os
import discord
from discord.ext import commands
from discord.ui import Select, View, Button

# --- CONFIGURAÇÕES DO BOT ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID do cargo de suporte principal puxado do Railway
ID_CARGO_SUPORTE = int(os.getenv("ID_CARGO_SUPORTE", 123456789012345678))

# --- LINKS DOS BANNERS E IMAGENS ---
URL_THUMBNAIL_TICKET = "https://i.imgur.com/8N4aQ8L.png"

# Banner enviado por você:
URL_BANNER_PAINEL_INICIAL = "https://cdn.discordapp.com/attachments/1536248865689440257/1536252370923687966/file_000000007968820eb5f30b80ea7a23f2.png?ex=6a7aba03&is=6a796883&hm=c022e2edccce5bd166703d948a6bbc7b2ed79d4444383b8ea4405345353f74f9&"
URL_BANNER_TICKET = "https://cdn.discordapp.com/attachments/1536248865689440257/1536252370923687966/file_000000007968820eb5f30b80ea7a23f2.png?ex=6a7aba03&is=6a796883&hm=c022e2edccce5bd166703d948a6bbc7b2ed79d4444383b8ea4405345353f74f9&"


# --- CONFIGURAÇÃO DE CANAIS POR OPÇÃO DE TICKET ---
CANAIS_OPCOES = {
    "suporte": 123456789012345678,         # ID do Canal de Suporte
    "reembolso": 123456789012345678,       # ID do Canal de Reembolso
    "receber_evento": 123456789012345678,  # ID do Canal de Eventos
    "vaga_mediador": 123456789012345678,   # ID do Canal de Mediadores
    "divulgacao": 123456789012345678      # ID do Canal de Divulgação
}


# --- VIEW DO PAINEL STAFF ---
class MenuPainelStaffView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ver Cargos com Acesso", style=discord.ButtonStyle.secondary, emoji="👥")
    async def ver_cargos(self, interaction: discord.Interaction, button: Button):
        cargo = interaction.guild.get_role(ID_CARGO_SUPORTE)
        nome_cargo = cargo.mention if cargo else "`Cargo não configurado`"
        
        embed = discord.Embed(
            title="👥 Cargos Marcados para Ver o Ticket",
            description=(
                f"**Cargo Principal de Suporte:** {nome_cargo}\n\n"
                "📌 **Nota:** Qualquer pessoa ou cargo que for **mencionado/marcado** dentro deste tópico "
                "terá permissão automática para visualizar e interagir no ticket."
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Puxar Transcript da Partida", style=discord.ButtonStyle.primary, emoji="📜")
    async def transcript_partida(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        
        mensagens = []
        async for msg in interaction.channel.history(limit=200, oldest_first=True):
            mensagens.append(f"[{msg.created_at.strftime('%d/%m/%Y %H:%M')}] {msg.author.name}: {msg.content}")

        if not mensagens:
            return await interaction.followup.send("Nenhuma mensagem encontrada para gerar o transcript.", ephemeral=True)

        conteudo = "\n".join(mensagens)
        nome_arquivo = f"transcript-{interaction.channel.name}.txt"

        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)

        arquivo = discord.File(nome_arquivo)
        await interaction.followup.send(content="📜 **Transcript gerado com sucesso:**", file=arquivo, ephemeral=True)
        os.remove(nome_arquivo)


# --- VIEW COM OS BOTÕES PRINCIPAIS DO TICKET ---
class PainelTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Assumir",
        style=discord.ButtonStyle.success,
        emoji="<:emoji_10:1536910081730412674>",
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
        emoji="<:emoji_9:1536910049870610624>",
        custom_id="btn_finalizar_ticket"
    )
    async def finalizar_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "🔒 **O ticket será DELETADO em 5 segundos...**"
        )
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.delete()

    @discord.ui.button(
        label="Painel Staff",
        style=discord.ButtonStyle.primary,
        emoji="<:emoji_2:1536869754944487486>",
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
            content="🛠️ **Painel Administrativo do Staff:**",
            view=MenuPainelStaffView(),
            ephemeral=True
        )


# --- DEFINIÇÃO DO MENU (SELECT) ---
class MenuAjudaSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Suporte",
                description="Clique aqui para abrir um chamado de suporte.",
                value="suporte",
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

        await interaction.response.send_message(
            content="**verificando...**",
            ephemeral=True
        )

        id_canal_destino = CANAIS_OPCOES.get(opcao, interaction.channel.id)
        canal_destino = interaction.guild.get_channel(id_canal_destino) or interaction.channel

        if opcao == "suporte":
            nome_topico = f"suporte-{usuario.name}"
        elif opcao == "reembolso":
            nome_topico = f"reembolso-{usuario.name}"
        elif opcao == "receber_evento":
            nome_topico = f"evento-{usuario.name}"
        elif opcao == "vaga_mediador":
            nome_topico = f"mediador-{usuario.name}"
        elif opcao == "divulgacao":
            nome_topico = f"divulgacao-{usuario.name}"

        # 1. Criação do Tópico Privado no canal escolhido
        topico = await canal_destino.create_thread(
            name=nome_topico,
            type=discord.ChannelType.private_thread,
            auto_archive_duration=1440
        )

        # 2. Embed do Ticket Privado (Com Banner e Thumbnail)
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
        embed_ticket.set_image(url=URL_BANNER_TICKET)

        # 3. Envia as menções + Embed + Botões no tópico
        await topico.send(
            content=f"{usuario.mention} <@&{ID_CARGO_SUPORTE}>",
            embed=embed_ticket,
            view=PainelTicketView()
        )

        # 4. Atualiza a mensagem ephemeral com o link do ticket
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


# --- COMANDO PARA ENVIAR O PAINEL INICIAL ---
@bot.command(name="painel")
@commands.has_permissions(administrator=True)
async def enviar_painel(ctx):
    embed = discord.Embed(
        title="Central de Atendimento",
        description="Escolha uma das opções abaixo para abrir um chamado privado:",
        color=discord.Color.blue()
    )
    embed.set_image(url=URL_BANNER_PAINEL_INICIAL)
    embed.set_footer(text="Selecione a opção no menu abaixo.")
    
    await ctx.send(embed=embed, view=MenuAjudaView())


# --- INICIALIZAÇÃO VIA VARIÁVEL DE AMBIENTE (RAILWAY) ---
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("ERRO CRÍTICO: A variável 'DISCORD_TOKEN' não foi configurada no Railway!")

bot.run(TOKEN)
