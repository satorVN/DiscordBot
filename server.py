import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Discord token from environment variable
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Thông tin tài khoản ngân hàng
BANK_NAME = 'NGO THANH NHAN'
BANK_NUMBER = '35620089999'
BANK_TYPE = 'MB Bank'

# Link ảnh QR của bạn (đã chuyển đổi)
CUSTOM_QR_IMAGE = 'https://drive.google.com/uc?id=1CrhD1hKYMqPp7hwqnM-hroOq0ichbWXe'

# Tạo bot với prefix và intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Khi bot online
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} đã sẵn sàng!')
    print(f'📱 Bot đang hoạt động trong {len(bot.guilds)} server')

# Lệnh bank
@bot.command()
async def bank(ctx):
    # Tạo embed đẹp với ảnh custom
    embed = discord.Embed(
        title="💳 THÔNG TIN TÀI KHOẢN NGÂN HÀNG",
        description="Thông tin chuyển khoản:",
        color=0x00ff00  # Màu xanh lá
    )

    embed.add_field(
        name="👤 Tên tài khoản",
        value=f"`{BANK_NAME}`",
        inline=False
    )
    embed.add_field(
        name="🏦 Ngân hàng",
        value=f"`{BANK_TYPE}`",
        inline=True
    )
    embed.add_field(
        name="🔢 Số tài khoản",
        value=f"`{BANK_NUMBER}`",
        inline=True
    )

    # Sử dụng ảnh QR custom của bạn
    embed.set_image(url=CUSTOM_QR_IMAGE)
    embed.set_footer(text="Quét QR code để chuyển khoản nhanh")

    await ctx.send(embed=embed)
    await ctx.message.add_reaction('💳')
    print(f"✅ Đã gửi thông tin bank cho {ctx.author}")

# Lệnh ping
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Độ trễ: {latency}ms')

# Lệnh help
@bot.command()
async def help(ctx):
    help_msg = """🤖 **HƯỚNG DẪN SỬ DỤNG BOT**

📝 **Các lệnh:**
• `!bank` - Xem thông tin tài khoản
• `!ping` - Kiểm tra độ trễ bot
• `!help` - Hiển thị menu này

💡 Bot sẽ tự động phản hồi khi bạn nhắn từ khóa!"""
    await ctx.send(help_msg)

# Xử lý lỗi command không tồn tại
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Lệnh không tồn tại! Dùng `!help` để xem danh sách lệnh.")
    else:
        print(f"❌ Lỗi: {error}")

# Main function to run the bot
def main():
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ LỖI: Token không đúng! Kiểm tra lại DISCORD_TOKEN trong biến môi trường.")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()