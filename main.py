import requests
import time
import os

finnhub_api = os.getenv("FINNHUB_API")
telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

stock_list = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

def get_rsi(symbol):
    url = f"https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&indicator=rsi&timeperiod=14&token={finnhub_api}"
    try:
        r = requests.get(url).json()
        return round(r["rsi"][-1], 2)
    except:
        return None

def get_macd_signal(symbol):
    url = f"https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&indicator=macd&token={finnhub_api}"
    try:
        r = requests.get(url).json()
        return r["macd"][-1], r["signal"][-1]
    except:
        return None, None

def check_positive_news(symbol):
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2023-08-01&to=2025-08-02&token={finnhub_api}"
    try:
        news_list = requests.get(url).json()
        keywords = ['growth', 'beat', 'strong', 'surge', 'record', 'positive', 'rally']
        for item in news_list:
            if any(word in item['headline'].lower() for word in keywords):
                return True
    except:
        pass
    return False

def evaluate_stock(symbol):
    rsi = get_rsi(symbol)
    macd, signal = get_macd_signal(symbol)
    news = check_positive_news(symbol)

    score = 0
    if rsi and rsi < 30: score += 1
    if macd and signal and macd > signal: score += 1
    if news: score += 1

    return {
        "symbol": symbol,
        "score": score,
        "rsi": rsi,
        "macd": macd,
        "signal": signal,
        "news_positive": news
    }

results = []
for stock in stock_list:
    print(f"🔍 تحليل {stock}...")
    results.append(evaluate_stock(stock))
    time.sleep(1)

best = sorted(results, key=lambda x: x["score"], reverse=True)[0]

parts = []
if best["rsi"] and best["rsi"] < 30:
    parts.append(f"RSI منخفض ({best['rsi']}) مما يدل على تشبع بيعي")
if best["macd"] and best["signal"] and best["macd"] > best["signal"]:
    parts.append("تقاطع MACD إيجابي")
if best["news_positive"]:
    parts.append("أخبار إيجابية حديثة")

explanation = "، و".join(parts) if parts else "البيانات الفنية لا تُظهر توصية واضحة"

message = f"""📈 توصية اليوم: سهم {best['symbol']}

✅ {explanation}

#OptScanX
"""

send_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
res = requests.post(send_url, data={"chat_id": telegram_chat_id, "text": message})

if res.status_code == 200:
    print("📬 تم إرسال التوصية بنجاح.")
else:
    print("❌ فشل الإرسال:", res.text)
