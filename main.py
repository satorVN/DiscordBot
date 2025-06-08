import discord
from discord.ext import commands
import asyncio
import os
import time

# Khai báo intents
intents = discord.Intents.default()
intents.message_content = True  # Bật quyền đọc nội dung tin nhắn
intents.messages = True        # Bật quyền đọc tin nhắn

# Thiết lập bot với tiền tố và intents
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot đã sẵn sàng với tên {bot.user} vào lúc {time.strftime("%H:%M:%S", time.localtime())}')

@bot.command()
async def bank(ctx):
    file_path = 'qr_image.jpg'  # Đường dẫn tới file ảnh
    if not os.path.exists(file_path):
        await ctx.send("Lỗi: Không tìm thấy file ảnh QR. Vui lòng kiểm tra lại!")
        return
    
    embed = discord.Embed(
        title="💸 Thông tin tài khoản",
        color=discord.Color.green()
    )
    embed.add_field(name="Tên tài khoản", value="**NGO THANH NHAN**", inline=False)
    embed.add_field(name="Số tài khoản", value="**35620089999**", inline=False)
    embed.add_field(name="Ngân hàng", value="**MB Bank**", inline=False)
    
    file = discord.File(file_path)
    embed.set_image(url=f"attachment://qr_image.jpg")

    await ctx.send(embed=embed, file=file)

# Hàm chạy bot
async def main():
    try:
        await bot.start("MTM4MTEwOTAzNzQwMzM0NDkxNw.GNiRFs.6iVNLLHYNZ42__Ev94dB-S_XXtVSsFO1aEnVGA")  # Thay bằng token bot của bạn
    except Exception as e:
        print(f"Lỗi khi khởi động bot: {e}")

# Chạy bot
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
    loop.close()
except Exception as e:
    print(f"Lỗi khi chạy bot: {e}")
