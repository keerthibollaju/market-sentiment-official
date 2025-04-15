from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import uuid
from config import PINECONE_API_KEY

pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "market-sentiment-memory"
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(INDEX_NAME)
model = SentenceTransformer('all-MiniLM-L6-v2')

def store_memory(user_id: str, content: str) -> None:
    embedding = model.encode(content).tolist()
    memory_id = str(uuid.uuid4())
    index.upsert(vectors=[{
        "id": memory_id,
        "values": embedding,
        "metadata": {"user_id": user_id, "content": content}
    }])

def retrieve_memory(user_id: str) -> str:
    results = index.query(
        vector=[0] * 384,
        filter={"user_id": user_id},
        top_k=5,
        include_metadata=True
    )
    memories = [match["metadata"]["content"] for match in results["matches"]]
    return "\n".join(memories) if memories else "No past context available."