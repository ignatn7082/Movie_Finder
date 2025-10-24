from dotenv import load_dotenv
import os

# Load biến môi trường từ .env
load_dotenv()

# (tùy chọn) kiểm tra API key đã load
print(" GEMINI_API_KEY loaded:", bool(os.getenv("GEMINI_API_KEY")))
