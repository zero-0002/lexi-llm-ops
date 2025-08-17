import pandas as pd
import re
import os
import numpy as np
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import Distance, PointStruct, FieldCondition, Filter, MatchValue
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


def is_valid_vector(vec, dim=1024):
    if vec is None or len(vec) != dim:
        return False
    if any(v is None or isinstance(v, str) or np.isnan(v) for v in vec):
        return False
    return True


def point_exists(qdrant, collection_name, cid, chunk_index):
    """Kiểm tra xem cid + chunk_index đã tồn tại chưa"""
    filt = Filter(
        must=[
            FieldCondition(key="cid", match=MatchValue(value=int(cid))),
            FieldCondition(key="chunk_index", match=MatchValue(value=int(chunk_index)))
        ]
    )
    result = qdrant.scroll(
        collection_name=collection_name,
        scroll_filter=filt,
        limit=1,
        with_payload=False,
        with_vectors=False
    )[0]
    return len(result) > 0


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

    # Nếu collection đã tồn tại thì giữ nguyên (không recreate để tránh mất dữ liệu)
    if collection_name not in [col.name for col in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
        print(f"✅ Created collection: {collection_name}")
    else:
        print(f"📂 Using existing collection: {collection_name}")

    # Generate point_id mới dựa trên số lượng đã có
    point_id = qdrant.count(collection_name=collection_name, exact=True).count
    batch = []

    for row in tqdm(df.itertuples(), total=len(df)):
        chunks = create_fixed_chunks(row.text)
        for i, chunk in enumerate(chunks):
            if point_exists(qdrant, collection_name, row.cid, i):
                continue  # skip trùng

            vec = model.encode(chunk)["dense_vecs"]
            if not is_valid_vector(vec):
                print(f"⚠️ Invalid vector: cid={row.cid}, chunk={i}")
                continue

            payload = {
                "cid": int(row.cid),
                "chunk_index": i,
                "text": chunk
            }
            point = PointStruct(id=point_id, vector=vec, payload=payload)
            batch.append(point)
            point_id += 1

            if len(batch) >= 20:
                qdrant.upsert(collection_name=collection_name, points=batch)
                batch = []

    # Don't forget the last batch
    if batch:
        qdrant.upsert(collection_name=collection_name, points=batch)

    print("✅ Done indexing corpus into Qdrant.")


# === RUN ===
corpus_csv = r"D:\Data\Legal-Retrieval\data\corpus.csv"
collection_name = "law_corpus_bge_v3"

index_corpus_to_qdrant(corpus_csv, collection_name)
