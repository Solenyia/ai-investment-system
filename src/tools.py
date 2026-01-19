import uuid
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
import re
import pandas as pd

load_dotenv("src/keys.env")

web_search = TavilySearch(max_results=5, topic="finance", search_depth="advanced")  # parametrizacia tavily searchu auto_parameters, default pre max_results = 5

def get_technical_signals(stock_symbol: str) -> str:
    """Loads historical data and summarizes key technical signals for LLM agents."""
    file_name = f"{stock_symbol.upper()}_historical_data.csv"
    
    try:
        # Load historical data
        df = pd.read_csv(file_name, index_col='Date', parse_dates=True)
        
        # Calculate key indicators
        latest_price = df['Close'].iloc[-1]
        ma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
        ma_200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        signals = []
        
        # Determine signals for debate
        if latest_price > ma_50 and latest_price > ma_200:
            signals.append("• **Bullish:** Price of the stock is above the 50-day and 200-day moving averages (strong upward trend).")
        elif latest_price < ma_50 and latest_price < ma_200:
            signals.append("• **Bearish:** Price of the stock is below the 50-day and 200-day moving averages (strong downward trend).")
        else:
            signals.append("• **Neutral:** Price is between key moving averages, indicating market indecision.")
        
        signals.append(f"• Current closing price: {latest_price:.2f}.")
        signals.append(f"• 50-day moving average (MA50): {ma_50:.2f}.")
        signals.append(f"• 200-day moving average (MA200): {ma_200:.2f}.")

        # Return summary for LLM
        return "--- TECHNICAL ANALYSIS ---\n" + "\n".join(signals)

    except FileNotFoundError:
        return f"TECHNICAL ANALYSIS: File {file_name} for stock {stock_symbol} not found. Only web information is available."
    except Exception as e:
        return f"TECHNICAL ANALYSIS: Error processing data for {stock_symbol}."

def search_and_extract_signals(
    stock_symbol: str, query: str, keywords: list[str], prefix: str, default_msg: str
) -> str:
    results = web_search.invoke(query)

    # --- Normalize Tavily output ---
    if isinstance(results, dict):
        results = results.get("results", [])

    elif isinstance(results, str):
        # Unexpected: agent system converted output to a string
        return f"{prefix} {stock_symbol}: No valid structured results returned"

    # Ensure results is iterable
    if not isinstance(results, list):
        return f"{prefix} {stock_symbol}: No valid search results"

    signals = []

    # --- Safe extraction ---
    for result in results:
        if not isinstance(result, dict):
            continue

        content = result.get("content", "").lower()
        title = result.get("title", "News")

        if any(word in content for word in keywords):
            signals.append(f"• {title}: {content[:200]}...")

    if signals:
        return f"{prefix} for {stock_symbol}:\n" + "\n".join(signals[:5])

    return f"{prefix} {stock_symbol}: {default_msg}"

    
    # POS signals

def get_positive_news(stock_symbol: str):
    """Search for positive news and developments about a stock"""
    keywords = ["growth", "profit", "upgrade", "buy", "bullish", "surge", "record high","strong", "strong returns", "exceed expectations", "outperform"]
    prefix = "Positive signals"
    default_msg = "No significant positive signals found"
    query = f"{stock_symbol} stock positive news"
    return search_and_extract_signals(stock_symbol, query, keywords, prefix, default_msg)

def get_negative_news(stock_symbol: str):
    """Search for negative news and risks about a stock"""
    keywords = ["decline", "loss", "downgrade", "sell", "bearish", "plunge", "lawsuit","weak", "miss expectations", "underperform"]
    prefix = "Negative signals"
    default_msg = "No significant negative signals found"
    query = f"{stock_symbol} stock negative news"
    return search_and_extract_signals(stock_symbol, query, keywords, prefix, default_msg)

def get_market_sentiment(stock_symbol: str):
    """Get overall market sentiment and recent performance."""
    
    keywords = [
        "fear", "uncertainty", "volatility", 
        "optimism", "confidence", "risk-on", "risk-off"
    ]
    prefix = "Market sentiment signals"
    default_msg = "No significant market sentiment signals found"
    query = f"{stock_symbol} stock market sentiment"

    results = web_search.invoke(query)

    # --- Normalize Tavily output ---
    if isinstance(results, dict):
        # Tavily sometimes returns: { "results": [ {...}, {...} ] }
        results = results.get("results", [])

    elif isinstance(results, str):
        # LangGraph may convert the whole list to a string
        return f"{prefix} {stock_symbol}: No valid structured results returned"

    # Ensure results is a list
    if not isinstance(results, list):
        return f"{prefix} {stock_symbol}: No valid search results"

    sentiment_signals = []

    # --- Safe extraction ---
    for result in results:
        if not isinstance(result, dict):
            continue  # ignore strings or unexpected items

        content = result.get("content", "").lower()
        title = result.get("title", "News")

        if any(word in content for word in keywords):
            sentiment_signals.append(f"• {title}: {content[:200]}...")

    # --- If signals were found ---
    if sentiment_signals:
        return f"{prefix} for {stock_symbol}:\n" + "\n".join(sentiment_signals[:2])

    # --- If no signals were found ---
    return f"{prefix} {stock_symbol}: {default_msg}"


def make_decision(
    stock_symbol: str,
    positive_news: str,
    negative_news: str,
):
    """Make final investment decision based on extracted signals"""
    def count_bullets(text: str) -> int:
        return len(re.findall(r"•", text)) if "•" in text else 1
    
    def check_signals(text: str, keywords: list[str]) -> bool:
        return any(word in text.lower() for word in keywords)

    #score calculation
    pos__score = count_bullets(positive_news)
    neg_score = count_bullets(negative_news)

    # Signal detection
    strong_pos_signals = check_signals(positive_news, ["growth", "profit", "upgrade", "buy", "bullish"])
    strong_neg_signals = check_signals(negative_news, ["decline", "loss", "downgrade", "sell", "bearish"])


    if pos__score > neg_score and strong_pos_signals:
        decision = "BUY"
        reasoning = f"The positive news outweighs the negative news for {stock_symbol}."
    elif neg_score > pos__score and strong_neg_signals:
        decision = "SELL/AVOID"
        reasoning = f"The negative news outweighs the positive news for {stock_symbol}."
    else:
        decision = "HOLD"
        reasoning = f"The positive and negative news are balanced for {stock_symbol}."

    return (
        f"FINAL DECISION for {stock_symbol} >> {decision}\n"
        f"REASONING: {reasoning}\n\n"
        f"Positive Agent> {positive_news} points\n\n"
        f"Negative Agent> {negative_news} points\n\n"
        f"Reccomended Action: {decision.lower()}"
    )