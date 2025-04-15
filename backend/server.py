from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tools import check_news_sentiment, analyze_market_trend
from memory import store_memory, retrieve_memory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://market-sentiment-frontend-e56gkqjo-keerthibollaju-projects.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tools = {"check_sentiment": check_news_sentiment, "analyze_market_trend": analyze_market_trend}

class QueryRequest(BaseModel):
    user_id: str
    query: str

@app.get("/")
async def root():
    return {"message": "Market Sentiment Agent API. Use POST /query to interact."}

@app.post("/query")
async def run_agent(request: QueryRequest):
    user_id = request.user_id
    query = request.query

    filler_words = {"what", "is", "the", "current", "sentiment", "around", "are", "latest", "trends", "in"}
    keywords = " ".join(
        word.strip("?.!,")
        for word in query.lower().split()
        if word.strip("?.!,") not in filler_words and word.strip("?.!,")
    ).strip()

    if "sentiment" in query.lower():
        response = tools["check_sentiment"].invoke(keywords or "tech")
    elif "trend" in query.lower() or "sector" in query.lower():
        symbol = "XOM" if "energy" in query.lower() else "AAPL"
        response = tools["analyze_market_trend"].invoke(symbol)
    else:
        response = "I can check news sentiment or market trends. Try asking about those!"

    past_context = retrieve_memory(user_id)
    full_response = f"Past context: {past_context}\nCurrent response: {response}"
    store_memory(user_id, f"Query: {query}\nResponse: {response}")
    return {"response": full_response}

@app.delete("/memory/{user_id}")
async def clear_memory(user_id: str):
    from memory import index  # Import here to avoid circular imports
    results = index.query(
        vector=[0] * 384,
        filter={"user_id": user_id},
        top_k=1000,
        include_metadata=False
    )
    ids = [match["id"] for match in results["matches"]]
    if ids:
        index.delete(ids=ids)
    return {"message": "Memory cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)