import ccxt

exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '5m'

# گرفتن ۲ کندل آخر
candles = exchange.fetch_ohlcv(symbol, timeframe, limit=2)

current_candle = candles[-1] 
timestamp, open_, high, low, close, volume = current_candle

# چک می‌کنیم که این کندل هنوز بسته نشده؟
import time
now = exchange.milliseconds()
candle_duration = 5 * 60 * 1000  # ۵ دقیقه به میلی‌ثانیه
if now - timestamp < candle_duration:
    print("کندل جاری پیدا شد:", current_candle)
else:
    print("کندل بسته شده، باید منتظر کندل بعدی بمونیم یا با ticker بسازیمش")
