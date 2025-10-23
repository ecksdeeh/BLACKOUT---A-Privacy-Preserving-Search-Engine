from fastapi import FastAPI, Query
from dotenv import load_dotenv
from serpapi import GoogleSearch
import random, os

# Load environment variables
load_dotenv()

app = FastAPI(title="Private Search Engine API", description="Privacy-preserving search using SerpAPI and decoy queries")

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# --- Decoy generator ---
def generate_decoys(user_query):
    words = user_query.split()
    decoys = []
    for word in words:
        if len(word) > 3:
            decoys.append(word[::-1])  # reversed word
    decoy_phrases = [
        user_query + " history",
        user_query + " tutorial",
        "how to " + user_query,
        "latest news about " + random.choice(words)
    ]
    return random.sample(decoys + decoy_phrases, k=min(3, len(decoys) + len(decoy_phrases)))

# --- Real search function ---
def perform_search(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])

@app.get("/")
def root():
    return {"message": "Private Search Engine API is running 🚀"}

@app.get("/search")
def private_search(query: str = Query(..., description="User's actual search query")):
    # Generate decoy queries
    decoys = generate_decoys(query)
    all_queries = [query] + decoys

    # Perform all searches
    results = {}
    for q in all_queries:
        results[q] = perform_search(q)

    return {
        "real_query": query,
        "decoys": decoys,
        "results_count": {q: len(results[q]) for q in all_queries},
        "sample_results": results[query][:3]  # show top 3 for demo
    }

# Run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
