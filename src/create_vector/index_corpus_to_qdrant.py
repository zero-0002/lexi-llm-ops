import pandas as pd
import re
import os
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from FlagEmbedding import BGEM3FlagModel

def get_qdrant_url():
    """Get Qdrant URL with environment support"""
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        namespace = os.getenv('NAMESPACE', 'default')
        return f"http://qdrant.{namespace}.svc.cluster.local:6333"
    
    # For Docker Compose, try to resolve qdrant hostname
    try:
        import socket
        socket.gethostbyname('qdrant')
        return "http://qdrant:6333"
    except:
        return "http://localhost:6333"

def create_fixed_chunks(text, max_word_count=400):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current_chunk, word_count = [], "", 0
    for sentence in sentences:
        wc = len(sentence.split())
        if word_count + wc > max_word_count:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk, word_count = sentence, wc
        else:
            current_chunk += " " + sentence if current_chunk else sentence
            word_count += wc
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks



def index_corpus_to_qdrant(corpus_path: str, collection_name: str):
    # Load data
    df = pd.read_csv(corpus_path)
    print(f"Loaded {len(df)} corpus entries")

    # Init model
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)

    # Init Qdrant with proper URL resolution
    qdrant_url = get_qdrant_url()
    print(f"🔗 Connecting to Qdrant at: {qdrant_url}")
    qdrant = QdrantClient(url=qdrant_url)

    # Create collection
    vector_size = 1024  # BGEM3 output dim
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    # Build points
    points = []
    point_id = 0
    for row in tqdm(df.itertuples(), total=len(df)):
        chunks = create_fixed_chunks(row.text)
        for i, chunk in enumerate(chunks):
            vec = model.encode(chunk)["dense_vecs"]
            payload = {
                "cid": int(row.cid),
                "chunk_index": i,
                "text": chunk
            }
            points.append(PointStruct(id=point_id, vector=vec, payload=payload))
            point_id += 1

    # Upsert to Qdrant
    print(f"Uploading {len(points)} vectors to Qdrant...")
    qdrant.upsert(collection_name=collection_name, points=points)
    print("✅ Done indexing corpus into Qdrant.")

corpus_csv = r"D:\Data\Legal-Retrieval\data\corpus.csv"
collection_name = "law_corpus_bge"

index_corpus_to_qdrant(corpus_csv, collection_name)
