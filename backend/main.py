from tools import check_news_sentiment, analyze_market_trend
from memory import store_memory, retrieve_memory

tools = {"check_sentiment": check_news_sentiment, "analyze_market_trend": analyze_market_trend}

def run_agent(user_id: str, query: str) -> str:
    # Retrieve past context
    past_context = retrieve_memory(user_id)
    
    # Improved keyword extraction: remove punctuation and filter filler words
    filler_words = {"what", "is", "the", "current", "sentiment", "around", "are", "latest", "trends", "in"}
    keywords = " ".join(
        word.strip("?.!,")  # Remove common punctuation
        for word in query.lower().split()
        if word.strip("?.!,") not in filler_words and word.strip("?.!,")  # Only keep non-filler words
    ).strip()
    
    # Simple query routing
    if "sentiment" in query.lower():
        response = tools["check_sentiment"].invoke(keywords or "tech")  # Fallback to "tech" if keywords empty
    elif "trend" in query.lower() or "sector" in query.lower():
        symbol = "XOM" if "energy" in query.lower() else "AAPL"
        response = tools["analyze_market_trend"].invoke(symbol)
    else:
        response = "I can check news sentiment or market trends. Try asking about those!"
    
    # Combine with context
    full_response = f"Past context: {past_context}\nCurrent response: {response}"
    
    # Store new conversation
    store_memory(user_id, f"Query: {query}\nResponse: {response}")
    return full_response

if __name__ == "__main__":
    user_id = "user123"
    while True:
        query = input("Ask me anything (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        print(run_agent(user_id, query))
        
    