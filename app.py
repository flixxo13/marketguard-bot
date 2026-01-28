import streamlit as st
import yfinance as yf
import pandas as pd
from textblob import TextBlob

# 1. Seite konfigurieren
st.set_page_config(page_title="MarketGuard AI", page_icon="📈", layout="wide")

# 2. Titel und Header
st.title("🚀 MarketGuard AI Dashboard")
st.markdown("---")

# 3. Deine Aktienliste
ticker_list = ["NVDA", "AAPL", "TSLA", "MSFT", "SAP.DE"]

# 4. Funktion zum Datenabruf
def get_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Holt die letzten 5 Tage für stabilere Daten
        df = ticker.history(period="5d")
        if df.empty: return None
        
        # Einfaches Sentiment aus News
        news = ticker.news
        sentiment = "⚪ Neutral"
        if news:
            polarity = TextBlob(news[0]['title']).sentiment.polarity
            if polarity > 0.1: sentiment = "🟢 Positiv"
            elif polarity < -0.1: sentiment = "🔴 Negativ"
            
        return {
            "price": df['Close'].iloc[-1],
            "change": ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
            "history": df['Close'],
            "sentiment": sentiment
        }
    except:
        return None

# 5. Dashboard-Raster erstellen
cols = st.columns(2)

for i, ticker in enumerate(ticker_list):
    data = get_data(ticker)
    with cols[i % 2]:
        with st.container(border=True):
            if data:
                # Preis-Anzeige
                st.metric(
                    label=f"{ticker} ({data['sentiment']})", 
                    value=f"{data['price']:.2f} €", 
                    delta=f"{data['change']:.2f}%"
                )
                # Kleiner Chart
                st.line_chart(data['history'], height=150)
            else:
                st.error(f"Daten für {ticker} nicht verfügbar.")

st.markdown("---")
st.caption("Datenquelle: Yahoo Finance | Stand: 2026")
