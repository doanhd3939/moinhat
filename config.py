"""
Cấu hình dự án: quản lý biến môi trường, cấu hình mặc định.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8029254946:AAE8Upy5LoYIYsmcm8Y117Esm_-_MF0-ChA")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
ADMIN_IDS = set(map(int, os.environ.get("ADMIN_IDS", "7509896689").split(",")))
