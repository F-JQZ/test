import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN")
    exit()

ALLOWED_ROLE_NAME = "k"
STREAM_LINK = "https://www.twitch.tv/king"
STREAM_NAME = "KINGS!"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def has_allowed_role(interaction: discord.Interaction) -> bool:
    return any(role.name == ALLOWED_ROLE_NAME for role in interaction.user.roles)

@tree.command(
    name="send",
    description="إرسال رسالة منسقة في قناة معينة"
)
@app_commands.describe(
    channel="القناة المراد الإرسال فيها",
    title="عنوان الإعلان",
    message="نص الإعلان",
    footer="نص سفلي (اختياري)"
)
async def send(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    title: str,
    message: str,
    footer: str = None
):
    if not has_allowed_role(interaction):
        await interaction.response.send_message(
            f"❌ ليس لديك الصلاحية. تحتاج إلى رتبة `{ALLOWED_ROLE_NAME}`.",
            ephemeral=True
        )
        return

    # تنسيق الرسالة مثل
    embed = discord.Embed(
        title=title,
        description=message,
        color=discord.Color.dark_red()
    )
    
    if footer:
        embed.set_footer(text=footer)
    
    embed.set_author(name=interaction.guild.name)
    
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ تم إرسال الإعلان في #{channel.name}", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    await bot.change_presence(
        activity=discord.Streaming(
            name=STREAM_NAME,
            url=STREAM_LINK
        )
    )
    print(f"[+] Bot is ready as {bot.user}")

bot.run(TOKEN)
