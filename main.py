import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, Button, ChannelSelect, RoleSelect

# --- CONFIGURAÇÕES DO BOT ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# URL do Banner e Thumbnail (mesmo link)
URL_BANNER = "https://cdn.discordapp.com/attachments/1536248865689440257/1536252370923687966/file_000000007968820eb5f30b80ea7a23f2.png?ex=6a7aba03&is=6a796883&hm=c022e2edccce5bd166703d948a6bbc7b2ed79d4444383b8ea4405345353f74f9&"

# --- ESTRUTURA DE CONFIGURAÇÕES EM MEMÓRIA ---
# Essas variáveis armazenam as preferências definidas via /config_bot_ticket
CONFIG = {
    "canais_topicos": [],      # Lista de IDs de canais selecionados (até 5)
    "cargos_marcados": [],     # Lista de IDs de cargos marcados (até 10)
    "cargos_staff": []         # Lista de IDs de cargos com acesso às ações de Staff
}


# --- VIEW DO PAINEL STAFF ---
class MenuPainelStaffView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ver Cargos com Acesso", style=discord.ButtonStyle.secondary, emoji="👥")
    async def ver_cargos(self, interaction: discord.Interaction, button: Button):
        cargos_mencao = [f"<@&{cid}>" for cid in CONFIG["cargos_marcados"]]
        cargos_texto = ", ".join(cargos_mencao) if cargos_mencao else "`Nenhum cargo configurado`"
        
        embed = discord.Embed(
            title="👥 Cargos Marcados para Ver o Ticket",
            description=(
                f"**Cargos Notificados:** {cargos_texto}\n\n"
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


# --- VIEW DE AÇÕES DO TICKET (DENTRO DO TÓPICO) ---
class PainelTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    def e_staff(self, user: discord.Member) -> bool:
        if user.guild_permissions.administrator:
            return True
        return any(role.id in CONFIG["cargos_staff"] for role in user.roles)

    @discord.ui.button(
        label="Assumir",
        style=discord.ButtonStyle.success,
        emoji="<:emoji_10:1536910081730412674>",
        custom_id="btn_assumir_ticket"
    )
    async def assumir_callback(self, interaction: discord.Interaction, button: Button):
        if not self.e_staff(interaction.user):
            return await interaction.response.send_message(
                "Apenas membros da equipe permitida podem assumir este ticket!",
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
        if not self.e_staff(interaction.user):
            return await interaction.response.send_message(
                "Apenas membros da equipe permitida podem finalizar este ticket!",
                ephemeral=True
            )

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
        if not self.e_staff(interaction.user):
            return await interaction.response.send_message(
                "Você não tem permissão para acessar o Painel Staff.",
                ephemeral=True
            )

        await interaction.response.send_message(
            content="🛠️ **Painel Administrativo do Staff:**",
            view=MenuPainelStaffView(),
            ephemeral=True
        )


# --- MENU DE SELEÇÃO DE ATENDIMENTO ---
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

        # REGRA: Limitação de 1 ticket ativo por usuário
        for thread in interaction.guild.threads:
            if thread.name.endswith(f"-{usuario.name}") and not thread.archived:
                return await interaction.response.send_message(
                    "❌ **Você já possui um ticket em andamento!** Finalize o ticket atual antes de abrir outro.",
                    ephemeral=True
                )

        await interaction.response.send_message(
            content="**verificando...**",
            ephemeral=True
        )

        # Escolhe o canal apropriado com base nos canais configurados
        canal_destino = interaction.channel
        if CONFIG["canais_topicos"]:
            canal_destino = interaction.guild.get_channel(CONFIG["canais_topicos"][0]) or interaction.channel

        nome_topico = f"{opcao}-{usuario.name}"

        # 1. Cria o Tópico Privado
        topico = await canal_destino.create_thread(
            name=nome_topico,
            type=discord.ChannelType.private_thread,
            auto_archive_duration=1440
        )

        # 2. Monta as menções de cargos configurados
        mencoes_cargos = " ".join([f"<@&{cid}>" for cid in CONFIG["cargos_marcados"]])
        conteudo_mencao = f"{usuario.mention} {mencoes_cargos}".strip()

        # 3. Embed do Ticket (Banner + Thumbnail idênticos)
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
        embed_ticket.set_thumbnail(url=URL_BANNER)
        embed_ticket.set_image(url=URL_BANNER)

        # 4. Envia a mensagem no tópico com botões
        await topico.send(
            content=conteudo_mencao,
            embed=embed_ticket,
            view=PainelTicketView()
        )

        # 5. Atualiza a confirmação ao usuário
        await interaction.edit_original_response(
            content=f"ticket criado com sucesso! {topico.mention}"
        )


class MenuAjudaView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MenuAjudaSelect())


# --- VIEWS E MENUS DO COMANDO SLASH DE CONFIGURAÇÃO ---
class ConfigBotView(View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(
        cls=ChannelSelect,
        placeholder="Em qual canal vai criar cada tópico? (Até 5 canais)",
        min_values=1,
        max_values=5,
        channel_types=[discord.ChannelType.text]
    )
    async def select_canais(self, interaction: discord.Interaction, select: ChannelSelect):
        CONFIG["canais_topicos"] = [channel.id for channel in select.values]
        await interaction.response.send_message(
            f"✅ **Canais configurados:** {', '.join([c.mention for c in select.values])}",
            ephemeral=True
        )

    @discord.ui.select(
        cls=RoleSelect,
        placeholder="Quais cargos serão marcados no ticket? (Até 10 cargos)",
        min_values=1,
        max_values=10
    )
    async def select_cargos_marcados(self, interaction: discord.Interaction, select: RoleSelect):
        CONFIG["cargos_marcados"] = [role.id for role in select.values]
        await interaction.response.send_message(
            f"✅ **Cargos a serem marcados:** {', '.join([r.mention for r in select.values])}",
            ephemeral=True
        )

    @discord.ui.select(
        cls=RoleSelect,
        placeholder="Quem pode assumir, finalizar e acessar o painel staff?",
        min_values=1,
        max_values=10
    )
    async def select_cargos_staff(self, interaction: discord.Interaction, select: RoleSelect):
        CONFIG["cargos_staff"] = [role.id for role in select.values]
        await interaction.response.send_message(
            f"✅ **Cargos de Staff com permissão:** {', '.join([r.mention for r in select.values])}",
            ephemeral=True
        )


# --- COMANDO SLASH DE CONFIGURAÇÃO ---
@bot.tree.command(name="config_bot_ticket", description="Configura os canais, cargos e permissões do sistema de ticket.")
@app_commands.default_permissions(administrator=True)
async def config_bot_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚙️ Configuração do Sistema de Ticket",
        description=(
            "Use os menus abaixo para personalizar a operação do bot:\n\n"
            "1️⃣ **Canais dos Tópicos:** Selecione até 5 canais onde os tópicos poderão ser criados.\n"
            "2️⃣ **Cargos Marcados:** Escolha até 10 cargos notificados na abertura do ticket.\n"
            "3️⃣ **Permissão Staff:** Escolha quem pode gerenciar (assumir, finalizar, abrir painel staff).\n\n"
            "📌 *Limitação Ativa:* **Só é permitido 1 ticket por usuário por vez.**"
        ),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=URL_BANNER)
    
    await interaction.response.send_message(
        embed=embed,
        view=ConfigBotView(),
        ephemeral=True
    )


# --- EVENTOS E SYNC DE COMANDOS SLASH ---
@bot.event
async def on_ready():
    bot.add_view(MenuAjudaView())
    bot.add_view(PainelTicketView())
    try:
        synced = await bot.tree.sync()
        print(f"Comandos slash sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar comandos slash: {e}")
    print(f"Bot online como {bot.user.name}!")


# --- COMANDO CONVENCIONAL PARA ENVIAR O PAINEL INICIAL ---
@bot.command(name="painel")
@commands.has_permissions(administrator=True)
async def enviar_painel(ctx):
    embed = discord.Embed(
        title="Central de Atendimento",
        description="Escolha uma das opções abaixo para abrir um chamado privado:",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=URL_BANNER)
    embed.set_image(url=URL_BANNER)
    embed.set_footer(text="Selecione a opção no menu abaixo.")
    
    await ctx.send(embed=embed, view=MenuAjudaView())


# --- INICIALIZAÇÃO VIA VARIÁVEL DE AMBIENTE ---
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("ERRO CRÍTICO: A variável 'DISCORD_TOKEN' não foi configurada!")

bot.run(TOKEN)
        
