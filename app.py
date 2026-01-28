import sys
import time
import requests
# Fix für Pydroid 3
sys.modules['curl_cffi'] = None 

import telebot
import yfinance as yf
from textblob import TextBlob

# --- DEINE DATEN ---
TOKEN = "8525741494:AAHI_t0CjlelRFQWKMDH4ISprI1Ccwaz54c"
CHAT_ID = "2056047495"
mein_depot = ["NVDA", "AAPL", "SAP.DE", "TSLA", "MSFT"]

bot = telebot.TeleBot(TOKEN)

# --- DER TRICK: Wir geben uns als Browser aus ---
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

def get_market_data():
    report = "📊 *MarketGuard Live-Check*\n"
    report += "----------------------------\n"
    
    for symbol in mein_depot:
        try:
            # Wir nutzen die Session mit dem Browser-Header
            ticker = yf.Ticker(symbol, session=session)
            # Wir fragen die letzten 7 Tage ab, um Lücken am Morgen zu füllen
            data = ticker.history(period="7d", interval="1d")
            
            if not data.empty:
                last_price = data['Close'].iloc[-1]
                # Kurs vom Vortag für die %-Berechnung
                prev_price = data['Close'].iloc[-2] if len(data) > 1 else last_price
                change = ((last_price - prev_price) / prev_price) * 100
                
                # News Sentiment (sehr simpel gehalten)
                sentiment_icon = "⚪"
                try:
                    news = ticker.news
                    if news:
                        analysis = TextBlob(news[0]['title']).sentiment.polarity
                        if analysis > 0.1: sentiment_icon = "🟢"
                        elif analysis < -0.1: sentiment_icon = "🔴"
                except: pass
                
                trend = "📈" if change >= 0 else "📉"
                report += f"{sentiment_icon} *{symbol}*: {last_price:.2f} ({change:+.2f}%)\n"
            else:
                report += f"⚪ *{symbol}*: Derzeit keine Daten\n"
            
            # 2 Sekunden warten, um nicht aufzufallen
            time.sleep(2)
            
        except Exception as e:
            report += f"⚠️ *{symbol}*: API-Pause...\n"
            print(f"Fehler: {e}")
            
    return report

# --- BEFEHLE ---

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(CHAT_ID, "Bot aktiv! Schreib 'check' für deine Kurse.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = message.text.lower()
    
    if "check" in text:
        bot.send_message(CHAT_ID, "⏳ Ich frage die Kurse ab (Browser-Modus)...")
        try:
            msg = get_market_data()
            bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(CHAT_ID, "Fehler beim Abruf. Bitte IP wechseln (Flugmodus).")
            print(f"Fehler: {e}")
            
    elif "list" in text:
        bot.send_message(CHAT_ID, f"📋 Deine Liste: {', '.join(mein_depot)}")

if __name__ == "__main__":
    print("--- Bot läuft (Browser-Simulation aktiv) ---")
    bot.infinity_polling()

