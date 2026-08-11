import discord
from discord.ext import commands
import os
import asyncio

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
        if self.values[0] == "suporte":
            user = interaction.user
            channel = interaction.channel
            thread_name = f"suporte-{user.name}"

            # Verifica se o usuário já tem um tópico aberto
            existing_thread = discord.utils.get(channel.threads, name=thread_name)
            if existing_thread:
                await interaction.response.send_message(
                    f"Você já possui um tópico de suporte aberto: {existing_thread.mention}", 
                    ephemeral=True
                )
                return

            # Cria o tópico no canal do painel
            thread = await channel.create_thread(
                name=thread_name,
                auto_archive_duration=1440,
                type=discord.ChannelType.public_thread
            )

            # Adiciona o usuário no tópico
            await thread.add_user(user)

            # Aguarda 1 segundo e apaga a mensagem do sistema ("Bot adicionou Fulano ao tópico")
            await asyncio.sleep(1)
            async for message in thread.history(limit=5):
                if message.type == discord.MessageType.recipient_add:
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        pass # Bot precisa da permissão 'Gerenciar Mensagens' no canal
                    break

            # Envia a mensagem do ticket
            embed_ticket = discord.Embed(
                title="🛠️ Atendimento de Suporte",
                description=f"Olá {user.mention}, seja bem-vindo ao seu suporte!\nDescreva o seu problema ou dúvida abaixo que a equipe já vai te atender.",
                color=discord.Color.from_rgb(255, 20, 147)
            )
            await thread.send(embed=embed_ticket)

            # Responde o usuário no canal principal
            await interaction.response.send_message(
                f"Seu tópico de suporte foi criado com sucesso: {thread.mention}", 
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
    
