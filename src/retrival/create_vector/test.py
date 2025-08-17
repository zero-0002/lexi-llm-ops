import pandas as pd
import re
import os
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import PointStruct
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


def load_indexed_cids(log_path="indexed_cids.txt"):
    if not os.path.exists(log_path):
        return set()
    with open(log_path, "r") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())


def save_indexed_cid(cid, log_path="indexed_cids.txt"):
    with open(log_path, "a") as f:
        f.write(f"{cid}\n")


def get_next_point_id(qdrant, collection_name):
    # Lấy số lượng point đã index để tính point_id tiếp theo
    count = qdrant.count(collection_name=collection_name, exact=True).count
    return count


def index_corpus_to_qdrant(corpus_path: str, collection_name: str, log_path="indexed_cids.txt"):
    # Load data
    df = pd.read_csv(corpus_path)
    print(f"📄 Loaded {len(df)} corpus entries")

    # Init model
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)

    # Init Qdrant with proper URL resolution
    qdrant_url = get_qdrant_url()
    print(f"🔗 Connecting to Qdrant at: {qdrant_url}")
    qdrant = QdrantClient(url=qdrant_url)

    # Create collection if not exists
    if collection_name not in [col.name for col in qdrant.get_collections().collections]:
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
        print(f"🆕 Created collection `{collection_name}`")

    # Get already indexed cids from local log
    indexed_cids = load_indexed_cids(log_path)
    print(f"🔁 Resuming from last run: {len(indexed_cids)} cids already indexed")

    # Get next point ID from Qdrant
    point_id = get_next_point_id(qdrant, collection_name)

    batch = []
    for row in tqdm(df.itertuples(), total=len(df)):
        if row.cid in indexed_cids:
            continue  # skip đã xử lý

        try:
            chunks = create_fixed_chunks(row.text)
            for i, chunk in enumerate(chunks):
                vec = model.encode(chunk)["dense_vecs"]
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

            # Save sau mỗi row
            save_indexed_cid(row.cid, log_path)

        except Exception as e:
            print(f"❌ Error processing cid={row.cid}: {e}")
            continue

    # Final batch
    if batch:
        qdrant.upsert(collection_name=collection_name, points=batch)

    print("✅ Done indexing remaining corpus into Qdrant.")


# ----- MAIN -----
corpus_csv = r"D:\Data\Legal-Retrieval\data\corpus.csv"
collection_name = "law_corpus_bge"

index_corpus_to_qdrant(corpus_csv, collection_name)
