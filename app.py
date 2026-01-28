import streamlit as st
import yfinance as yf
import pandas as pd
from textblob import TextBlob

# Konfiguration der Web-App
st.set_page_config(page_title="MarketGuard AI", page_icon="📈", layout="wide")

# Styling für mobiles Design
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🚀 MarketGuard AI Dashboard")
st.write("Live-Überwachung deiner Favoriten (Stand: 2026)")

# Deine Aktienliste
ticker_list = ["NVDA", "AAPL", "TSLA", "MSFT", "SAP.DE"]

# Funktion für Datenabruf mit Fehlerbehandlung
def get_stock_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Wir holen 7 Tage, um Lücken am frühen Morgen oder Wochenende zu überbrücken
        df = ticker.history(period="7d")
        if df.empty:
            return None
        
        # News für Sentiment-Analyse abrufen
        news = ticker.news
        sentiment_score = 0
        if news:
            analysis = TextBlob(news[0]['title']).sentiment.polarity
            sentiment_score = analysis
            
        return {
            "price": df['Close'].iloc[-1],
            "prev_price": df['Close'].iloc[-2],
            "history": df['Close'],
            "sentiment": sentiment_score
        }
    except:
        return None

# Dashboard-Layout (2 Spalten auf dem Desktop, untereinander am Handy)
cols = st.columns(2)

for i, ticker in enumerate(ticker_list):
    info = get_stock_info(ticker)
    with cols[i % 2]:
        with st.container(border=True):
            if info:
                # Berechnung der Veränderung
                diff = info["price"] - info["prev_price"]
                percent = (diff / info["prev_price"]) * 100
                
                # Sentiment-Icon
                s_icon = "🟢" if info["sentiment"] > 0.1 else "🔴" if info["sentiment"] < -0.1 else "⚪"
                
                # Anzeige der Werte
                st.metric(
                    label=f"{s_icon} {ticker}", 
                    value=f"{info['price']:.2f} €", 
                    delta=f"{percent:.2f}%"
                )
                
                # Kleiner Trend-Chart
                st.line_chart(info["history"], height=150)
            else:
                st.error(f"Daten für {ticker} aktuell nicht verfügbar.")

st.divider()
st.info("💡 Tipp: Tippe im Browser auf die 3 Punkte und wähle 'Zum Startbildschirm hinzufügen', um diese App auf deinem Handy zu installieren.")
