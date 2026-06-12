import discord
from discord.ext import commands, tasks
from datetime import datetime

TOKEN = "MTUxNDk0ODM3NDAxNTc3NDc2MQ.Gxu8S4.FL8PlDfY7PC7xKHCg-tbceuXN5LvXSaxU-ZIC4"
CHANNEL_ID = 1514928208049602752  # ID del canale presenze

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

presenti = set()
messaggio_presenza = None


class PresenceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Presente",
        style=discord.ButtonStyle.success,
        emoji="✅"
    )
    async def presente(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = interaction.user.id

        if user_id in presenti:
            await interaction.response.send_message(
                "Hai già segnato la presenza!",
                ephemeral=True
            )
            return

        presenti.add(user_id)

        await interaction.response.send_message(
            "Presenza registrata!",
            ephemeral=True
        )

        embed = discord.Embed(
            title="📈 Presenze Trading",
            description=f"Presenti: {len(presenti)}",
            color=0x00ff00
        )

        global messaggio_presenza
        await messaggio_presenza.edit(embed=embed, view=self)


@tasks.loop(minutes=1)
async def controllo_orario():

    global presenti
    global messaggio_presenza

    ora = datetime.now()
    canale = bot.get_channel(CHANNEL_ID)

    if canale is None:
        return

    # 00:00 reset presenze
    if ora.hour == 0 and ora.minute == 0:
        presenti = set()

        embed = discord.Embed(
            title="📈 Presenze Trading",
            description="Presenti: 0",
            color=0x00ff00
        )

        view = PresenceView()

        messaggio_presenza = await canale.send(
            embed=embed,
            view=view
        )

    # 16:00 chiusura presenze
    if ora.hour == 16 and ora.minute == 0:

        lista = []
        for user_id in presenti:
            user = bot.get_user(user_id)
            if user:
                lista.append(user.mention)

        testo = "\n".join(lista) if lista else "Nessun presente"

        await canale.send(f"📋 Presenze chiuse.\n\n{testo}")


@bot.event
async def on_ready():
    print(f"Connesso come {bot.user}")
    controllo_orario.start()


bot.run(TOKEN)