name: Fetch Current 5m Candle

on:
  push:
    branches: [ main ]        # روی پوش به شاخه main اجرا شود
  schedule:
    - cron: '*/30 * * * *'    # هر ۳۰ دقیقه یک‌بار هم اجرا شود (اختیاری)
  workflow_dispatch:          # امکان اجرای دستی از تب Actions

jobs:
  run-script:
    runs-on: ubuntu-latest     # سیستم‌عامل لینوکس

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'   # یا نسخه دلخواه

      - name: Install dependencies
        run: pip install ccxt

      - name: Run script with unbuffered output
        env:
          PYTHONUNBUFFERED: 1      # پرینت‌ها بلافاصله در لاگ نمایش داده شوند
        run: python yt.py      # فایل پایتون شما
