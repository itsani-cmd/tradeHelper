import requests

BOT_TOKEN = "8162961504:AAHp24_bD5ayqdfx1-b1rLpLX9c7WQC0eU8"
CHAT_ID = "1274709265"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/"

}

def get_nifty_50_data():
    session = requests.Session()
    # Step 1: Get cookies by hitting the homepage first
    session.get("https://www.nseindia.com", headers=HEADERS)
    # Step 2: Now call the API with cookies and headers
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    response = session.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    stocks = data.get("data", [])

    results = []
    for stock in stocks:
        if stock.get("identifier") == "NIFTY 50":
            continue
        symbol = stock.get("symbol", "N/A")
        name = stock.get("meta", {}).get("companyName", "")
        current = stock.get("lastPrice", 0)
        low_52 = stock.get("yearLow", 0)
        results.append((symbol, name, current, low_52))
    return results

def format_nifty_report_by_ranges(data):
    groups = {
        "10% and below increase": [],
        "11% to 20% increase": [],
        "21% to 33% increase": []
    }

    for symbol, name, current, low_52 in data:
        try:
            pct = round((current - low_52) / low_52 * 100, 2)
        except Exception:
            pct = 0

        if 0 <= pct <= 10:
            group_key = "10% and below increase"
        elif 11 <= pct <= 20:
            group_key = "11% to 20% increase"
        elif 21 <= pct <= 33:
            group_key = "21% to 33% increase"
        else:
            continue

        line = f"{symbol} ({name}): ₹{current} | 52W Low: ₹{low_52} | +{pct}%\n\n"
        groups[group_key].append(line)

    messages = []
    for group_name, lines in groups.items():
        if lines:
            msg = f"📈 Stocks with {group_name}:\n\n" + "".join(lines)
            messages.append(msg)
    return messages

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.get(url, params=params)
    print("Telegram API response:", response.json())

if __name__ == "__main__":
    data = get_nifty_50_data()
    messages = format_nifty_report_by_ranges(data)
    for msg in messages:
        print("\n--- Sending message ---\n")
        print(msg)
        send_telegram_message(msg)
