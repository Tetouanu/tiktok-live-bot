FROM python:3.10-slim

# تحديث الحزم الضرورية ل Chromium
RUN apt-get update && apt-get install -y \
    wget \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libx11-xcb1 \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# تثبيت Playwright + Chromium
RUN pip install playwright
RUN playwright install --with-deps chromium

# إعداد مجلد التطبيق
WORKDIR /app
COPY . /app

# تثبيت مكتبات Python
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل السكريبت الرئيسي
CMD ["python", "tiktok_live_bot.py"]
