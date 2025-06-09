import discord
from discord.ext import commands
import os
import time
import requests
import io
import base64
from dotenv import load_dotenv
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tải biến môi trường
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
VIETQR_CLIENT_ID = os.getenv("VIETQR_CLIENT_ID")
VIETQR_API_KEY = os.getenv("VIETQR_API_KEY")
BANK_ACCOUNT = os.getenv("BANK_ACCOUNT")
BANK_CODE = os.getenv("BANK_CODE")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")

# Kiểm tra biến môi trường
if not DISCORD_TOKEN:
    logger.error("Thiếu DISCORD_TOKEN. Vui lòng kiểm tra biến môi trường.")
    exit(1)
if not all([VIETQR_CLIENT_ID, VIETQR_API_KEY, BANK_ACCOUNT, BANK_CODE, ACCOUNT_NAME]):
    logger.warning("Thiếu biến môi trường VietQR. Lệnh /noidung sẽ không hoạt động.")

# Cấu hình intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.messages = True

# Khởi tạo bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Hàng đợi phát nhạc (tạm thời vô hiệu để tránh lỗi FFmpeg)
queue = {}

# Sự kiện bot sẵn sàng
@bot.event
async def on_ready():
    print(f'Bot đã sẵn sàng: {bot.user} vào lúc {time.strftime("%H:%M:%S", time.localtime())}')
    try:
        synced = await bot.tree.sync()
        print(f"Đồng bộ {len(synced)} lệnh Slash.")
    except Exception as e:
        print(f"Lỗi khi đồng bộ lệnh Slash: {e}")

# --- Chức năng hiển thị thông tin ngân hàng ---

@bot.command(name='bank')
async def bank(ctx):
    file_path = 'qr_image.jpg'
    if not os.path.exists(file_path):
        await ctx.send(f"Lỗi: Không tìm thấy file QR tại {file_path}. Vui lòng upload file qr_image.jpg.")
        return

    try:
        file = discord.File(file_path)
        embed = discord.Embed(title="💸 Thông tin tài khoản", color=discord.Color.green())
        embed.add_field(name="Tên tài khoản", value="**NGO THANH NHAN**", inline=False)
        embed.add_field(name="Số tài khoản", value="**35620089999**", inline=False)
        embed.add_field(name="Ngân hàng", value="**MB Bank**", inline=False)
        embed.set_image(url=f"attachment://qr_image.jpg")
        await ctx.send(embed=embed, file=file)
    except Exception as e:
        await ctx.send(f"Lỗi khi gửi ảnh: {str(e)}")

# --- Chức năng tạo mã QR chuyển khoản ---

@bot.tree.command(name="noidung", description="Tạo mã QR chuyển khoản với số tiền và nội dung")
@app_commands.describe(amount="Số tiền chuyển khoản (VND)", content="Nội dung chuyển khoản")
@app_commands.checks.cooldown(1, 60)
async def noidung(interaction: discord.Interaction, amount: float, content: str):
    await interaction.response.defer()
    try:
        if not all([VIETQR_CLIENT_ID, VIETQR_API_KEY, BANK_ACCOUNT, BANK_CODE, ACCOUNT_NAME]):
            await interaction.followup.send("Lỗi: Thiếu thông tin API VietQR.")
            return

        if amount <= 0:
            await interaction.followup.send("Số tiền phải lớn hơn 0.")
            return
        if amount > 100000000:
            await interaction.followup.send("Số tiền quá lớn. Tối đa 100,000,000 VND.")
            return
        if len(content) > 100:
            await interaction.followup.send("Nội dung quá dài (tối đa 100 ký tự).")
            return
        if not content.isascii():
            await interaction.followup.send("Nội dung không được chứa ký tự tiếng Việt hoặc đặc biệt.")
            return

        payload = {
            "accountNo": BANK_ACCOUNT,
            "acqId": BANK_CODE,
            "accountName": ACCOUNT_NAME,
            "amount": int(amount),
            "addInfo": content,
            "template": "compact"
        }
        logger.info(f"Gửi payload tới VietQR: {payload}")

        vietqr_url = "https://api.vietqr.io/v2/generate"
        headers = {
            "x-client-id": VIETQR_CLIENT_ID,
            "x-api-key": VIETQR_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(vietqr_url, json=payload, headers=headers)

        if response.status_code != 200:
            error_msg = f"Lỗi: Không thể tạo mã QR. Mã lỗi: {response.status_code}"
            logger.error(f"Yêu cầu VietQR thất bại. Status: {response.status_code}, Response: {response.text}")
            await interaction.followup.send(error_msg[:1990] + "..." if len(error_msg) > 1990 else error_msg)
            return

        qr_data = response.json()
        qr_url = qr_data.get("data", {}).get("qrDataURL")
        if not qr_url or qr_url == "None":
            error_desc = qr_data.get("desc", "Không có thông tin lỗi")
            error_msg = f"Lỗi: Không thể tạo mã QR. Lý do: {error_desc}"
            logger.error(f"Không tìm thấy qrDataURL. Phản hồi: {qr_data}")
            await interaction.followup.send(error_msg[:1990] + "..." if len(error_msg) > 1990 else error_msg)
            return

        if qr_url.startswith("data:image/png;base64,"):
            base64_data = qr_url.split("data:image/png;base64,")[1]
            qr_image_data = base64.b64decode(base64_data)
            qr_file = discord.File(io.BytesIO(qr_image_data), filename="qrcode.png")
        else:
            qr_image_response = requests.get(qr_url)
            if qr_image_response.status_code != 200:
                logger.error(f"Tải hình ảnh QR thất bại. Status: {qr_image_response.status_code}")
                await interaction.followup.send("Lỗi: Không thể tải hình ảnh QR.")
                return
            qr_file = discord.File(io.BytesIO(qr_image_response.content), filename="qrcode.png")

        embed = discord.Embed(title="Mã QR Chuyển Khoản", color=discord.Color.green())
        embed.add_field(name="Số tiền", value=f"{amount:,.0f} VND", inline=False)
        embed.add_field(name="Nội dung", value=content, inline=False)
        embed.add_field(name="Số tài khoản", value=BANK_ACCOUNT, inline=False)
        embed.add_field(name="Ngân hàng", value=BANK_CODE, inline=False)
        embed.set_image(url="attachment://qrcode.png")

        await interaction.followup.send(embed=embed, file=qr_file)
    except Exception as e:
        error_msg = f"Lỗi: {str(e)}"
        logger.error(f"Lỗi không mong muốn: {str(e)}")
        await interaction.followup.send(error_msg[:1990] + "..." if len(error_msg) > 1990 else error_msg)

# Chạy bot
try:
    bot.run(DISCORD_TOKEN)
except Exception as e:
    logger.error(f"Lỗi khi chạy bot: {str(e)}")
    exit(1)