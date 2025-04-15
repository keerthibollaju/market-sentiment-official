from langchain.tools import tool
import requests
from config import NEWSAPI_KEY, FINNHUB_API_KEY
from statistics import mean
from datetime import datetime, timedelta

@tool
def check_news_sentiment(query: str) -> str:
    """Analyzes sentiment from multiple news articles and returns a summary with a score."""
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWSAPI_KEY}&pageSize=5"
    response = requests.get(url)
    data = response.json()
    articles = data.get("articles", [])
    if not articles:
        return f"No news found for '{query}'"

    positive_words = ["good", "rise", "success", "growth", "positive"]
    negative_words = ["bad", "fall", "decline", "loss", "negative"]
    sentiments = []
    summaries = []

    for article in articles:
        title = article.get("title", "").encode().decode("utf-8")
        desc = article.get("description", "")[:100].encode().decode("utf-8")
        text = (title + " " + desc).lower()
        score = sum(text.count(word) for word in positive_words) - sum(text.count(word) for word in negative_words)
        sentiments.append(score)
        summaries.append(f"{title[:50]}... - {desc}")

    avg_score = mean(sentiments) if sentiments else 0
    sentiment_label = "positive" if avg_score > 0 else "negative" if avg_score < 0 else "neutral"
    return f"News sentiment for '{query}': {sentiment_label} (score: {avg_score:.1f})\n" + "\n".join(summaries)

@tool
def analyze_market_trend(symbol: str) -> str:
    """Fetches current price and basic trend for a stock symbol."""
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    price = data.get("c", 0)
    prev_close = data.get("pc", 0)
    trend = "up" if price > prev_close else "down" if price < prev_close else "stable"
    return f"Latest price for {symbol}: {price:.2f} ({trend} from previous close: {prev_close:.2f})"

@tool
def forecast_market_trend(symbol: str) -> str:
    """Predicts short-term price movement based on recent candles."""
    end = datetime.now()
    start = end - timedelta(days=7)
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&from={int(start.timestamp())}&to={int(end.timestamp())}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data.get("s") == "no_data":
        return f"No recent data for {symbol}"
    
    closes = data.get("c", [])
    if len(closes) < 3:
        return f"Insufficient data for {symbol} forecast"
    
    recent_avg = mean(closes[-3:])
    older_avg = mean(closes[:-3])
    prediction = "likely to rise" if recent_avg > older_avg else "likely to fall" if recent_avg < older_avg else "stable"
    return f"Short-term forecast for {symbol}: {prediction} (based on recent 7-day trend)"