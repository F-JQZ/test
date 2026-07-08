import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

# ======== قراءة التوكن ========
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة.")
    exit()

# ======== إعدادات البوت ========
ALLOWED_ROLE_NAME = "k"
STREAM_LINK = "https://www.twitch.tv/king"
STREAM_NAME = "KINGS!"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ============================================
# دالة التحقق من الصلاحية
# ============================================
def has_allowed_role(interaction: discord.Interaction) -> bool:
    return any(role.name == ALLOWED_ROLE_NAME for role in interaction.user.roles)

# ============================================
# دالة مشتركة للإرسال
# ============================================
async def send_to_all(interaction: discord.Interaction, message: str, gap: str = "---"):
    # تنسيق الرسالة مع المسافة
    formatted_message = f"{gap}\n{message}\n{gap}"
    
    # إحصاء الأعضاء
    total_members = len(interaction.guild.members)
    members_without_bots = len([m for m in interaction.guild.members if not m.bot])
    
    # معاينة الرسالة
    preview = formatted_message[:500] + ("..." if len(formatted_message) > 500 else "")
    
    await interaction.response.send_message(
        f"📊 **إحصاء السيرفر:**\n"
        f"• إجمالي الأعضاء: {total_members}\n"
        f"• الأعضاء الحقيقيون (بدون بوتات): {members_without_bots}\n\n"
        f"📝 **معاينة الرسالة:**\n```\n{preview}\n```\n\n"
        f"📨 سيتم إرسالها للجميع في الخاص.\n"
        f"**اكتب `confirm` خلال 30 ثانية للتأكيد.**",
        ephemeral=True
    )

    # انتظار التأكيد
    def confirm_check(m):
        return m.author == interaction.user and m.channel == interaction.channel and m.content.lower() == "confirm"

    try:
        await bot.wait_for("message", timeout=30.0, check=confirm_check)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ تم الإلغاء (انتهى الوقت).", ephemeral=True)
        return

    # بدء الإرسال
    await interaction.followup.send(f"✅ جارٍ الإرسال إلى {members_without_bots} عضو في الخاص...", ephemeral=True)

    success = 0
    failed = 0

    for member in interaction.guild.members:
        if member.bot:
            continue

        try:
            await member.send(formatted_message)
            success += 1
            await asyncio.sleep(0.5)
        except:
            failed += 1

        if (success + failed) % 50 == 0:
            print(f"[*] تقدم: {success + failed}/{members_without_bots}")

    # النتيجة النهائية
    await interaction.followup.send(
        f"✅ **تم الانتهاء!**\n"
        f"✅ نجح الإرسال: {success}\n"
        f"❌ فشل الإرسال: {failed}\n"
        f"📊 المجموع: {members_without_bots}",
        ephemeral=True
    )

# ============================================
# الأمر test
# ============================================
@tree.command(
    name="test",
    description="إرسال رسالة لجميع أعضاء السيرفر في الخاص مع مسافة وإحصاء"
)
@app_commands.describe(
    message="النص الذي تريد إرساله",
    gap="المسافة (الإشارة) مثلاً: --- أو === (اختياري)"
)
async def test(interaction: discord.Interaction, message: str, gap: str = "---"):
    if not has_allowed_role(interaction):
        await interaction.response.send_message(
            f"❌ ليس لديك الصلاحية. تحتاج إلى رتبة `{ALLOWED_ROLE_NAME}`.",
            ephemeral=True
        )
        return
    
    await send_to_all(interaction, message, gap)

# ============================================
# الأمر all
# ============================================
@tree.command(
    name="all",
    description="إرسال رسالة لجميع أعضاء السيرفر في الخاص مع مسافة وإحصاء"
)
@app_commands.describe(
    message="النص الذي تريد إرساله",
    gap="المسافة (الإشارة) مثلاً: --- أو === (اختياري)"
)
async def all_command(interaction: discord.Interaction, message: str, gap: str = "---"):
    if not has_allowed_role(interaction):
        await interaction.response.send_message(
            f"❌ ليس لديك الصلاحية. تحتاج إلى رتبة `{ALLOWED_ROLE_NAME}`.",
            ephemeral=True
        )
        return
    
    await send_to_all(interaction, message, gap)

# ============================================
# تشغيل البوت
# ============================================
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
    print(f"[+] Slash commands synced!")
    print(f"[+] Streaming: {STREAM_NAME} -> {STREAM_LINK}")

bot.run(TOKEN)
