import discord
from discord.ext import commands
import asyncio
import os
import time
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot đã sẵn sàng với tên {bot.user} vào lúc {time.strftime("%H:%M:%S", time.localtime())}')

@bot.command()
async def bank(ctx):
    file_path = 'qr_image.jpg'
    if not os.path.exists(file_path):
        await ctx.send("Lỗi: Không tìm thấy file ảnh QR. Vui lòng kiểm tra lại!")
        return

    embed = discord.Embed(title="💸 Thông tin tài khoản", color=discord.Color.green())
    embed.add_field(name="Tên tài khoản", value="**NGO THANH NHAN**", inline=False)
    embed.add_field(name="Số tài khoản", value="**35620089999**", inline=False)
    embed.add_field(name="Ngân hàng", value="**MB Bank**", inline=False)

    file = discord.File(file_path)
    embed.set_image(url=f"attachment://qr_image.jpg")

    await ctx.send(embed=embed, file=file)

async def main():
    try:
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        print(f"Lỗi khi khởi động bot: {e}")

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
    loop.close()
except Exception as e:
    print(f"Lỗi khi chạy bot: {e}")
