import re
import uuid
import pandas as pd
from dotenv import load_dotenv
from langchain_core.tools import tool  # Správny import pre @tool
from langchain_tavily import TavilySearch

load_dotenv("src/keys.env")

# Inicializácia vyhľadávania
web_search = TavilySearch(max_results=5, topic="finance", search_depth="advanced")

# --- POMOCNÁ FUNKCIA (HELPER) ---
# Táto funkcia nemá dekorátor @tool, takže ju môžeme voľne volať v celom kóde.
def _core_web_search_logic(stock_symbol: str, query: str, keywords: list[str], prefix: str, default_msg: str) -> str:
    results = web_search.invoke(query)

    # Normalizácia výstupu z Tavily
    if isinstance(results, dict):
        results = results.get("results", [])
    elif isinstance(results, str):
        return f"{prefix} {stock_symbol}: No valid structured results returned"

    if not isinstance(results, list):
        return f"{prefix} {stock_symbol}: No valid search results"

    signals = []
    THRESHOLD = 0.75  # Prísny filter na kvalitu dát

    for result in results:
        if not isinstance(result, dict):
            continue

        score = result.get("score", 0)
        if score < THRESHOLD:
            continue

        content = result.get("content", "").lower()
        title = result.get("title", "News")

        if any(word in content for word in keywords):
            # Pridáme skóre do zátvorky pre agenta, aby videl relevanciu
            signals.append(f"• [Rel: {score:.2f}] {title}: {content[:200]}...")

    if signals:
        return f"{prefix} for {stock_symbol}:\n" + "\n".join(signals[:5])

    return f"{prefix} {stock_symbol}: {default_msg}"


# --- JEDNOTLIVÉ NÁSTROJE (TOOLS) ---

@tool("get_technical_signals")
def get_technical_signals(stock_symbol: str) -> str:
    """Loads historical data and summarizes key technical signals for LLM agents."""
    file_name = f"{stock_symbol.upper()}_historical_data.csv"
    
    try:
        df = pd.read_csv(file_name, index_col='Date', parse_dates=True)
        latest_price = df['Close'].iloc[-1]
        ma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
        ma_200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        signals = []
        if latest_price > ma_50 and latest_price > ma_200:
            signals.append("• **Bullish:** Price is above MA50 and MA200 (strong upward trend).")
        elif latest_price < ma_50 and latest_price < ma_200:
            signals.append("• **Bearish:** Price is below MA50 and MA200 (strong downward trend).")
        else:
            signals.append("• **Neutral:** Price is between key moving averages.")
        
        signals.append(f"• Current: {latest_price:.2f} | MA50: {ma_50:.2f} | MA200: {ma_200:.2f}")
        return "--- TECHNICAL ANALYSIS ---\n" + "\n".join(signals)

    except FileNotFoundError:
        return f"TECHNICAL ANALYSIS: File {file_name} for {stock_symbol} not found."
    except Exception as e:
        return f"TECHNICAL ANALYSIS: Error processing data: {str(e)}"


@tool("get_positive_news")
def get_positive_news(stock_symbol: str):
    """Search for positive news and developments about a stock"""
    keywords = ["growth", "profit", "upgrade", "buy", "bullish", "surge", "outperform"]
    query = f"{stock_symbol} stock positive news and growth catalysts"
    return _core_web_search_logic(stock_symbol, query, keywords, "Positive signals", "No significant positive signals found")


@tool("get_negative_news")
def get_negative_news(stock_symbol: str):
    """Search for negative news and risks about a stock"""
    keywords = ["decline", "loss", "downgrade", "sell", "bearish", "plunge", "weak"]
    query = f"{stock_symbol} stock negative news and risks"
    return _core_web_search_logic(stock_symbol, query, keywords, "Negative signals", "No significant negative signals found")


@tool("get_market_sentiment")
def get_market_sentiment(stock_symbol: str):
    """Get overall market sentiment and recent performance."""
    keywords = ["fear", "uncertainty", "volatility", "optimism", "confidence"]
    query = f"{stock_symbol} stock market sentiment analysis"
    return _core_web_search_logic(stock_symbol, query, keywords, "Market sentiment", "No significant sentiment found")


@tool("make_decision")
def make_decision(stock_symbol: str, positive_news: str, negative_news: str):
    """Make final investment decision based on extracted signals"""
    
    def count_bullets(text: str) -> int:
        found = re.findall(r"•|^\s*\d+\.|\n\s*\d+\.", text, re.MULTILINE)
        return len(found) if len(found) > 0 else 0
    
    def check_signals(text: str, keywords: list[str]) -> bool:
        return any(word in text.lower() for word in keywords)

    pos_score = count_bullets(positive_news)
    neg_score = count_bullets(negative_news)

    strong_pos = check_signals(positive_news, ["growth", "profit", "upgrade", "buy"])
    strong_neg = check_signals(negative_news, ["decline", "loss", "downgrade", "sell"])

    if pos_score > neg_score and strong_pos:
        decision = "BUY"
    elif neg_score > pos_score and strong_neg:
        decision = "SELL/AVOID"
    else:
        decision = "HOLD"

    return (
        f"--- FINAL DECISION FOR {stock_symbol.upper()} ---\n"
        f"DECISION: {decision}\n"
        f"REASONING: Positives ({pos_score}) vs Negatives ({neg_score})\n"
        f"Action: {decision.lower()}"
    )