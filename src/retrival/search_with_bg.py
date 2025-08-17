from typing import List, Dict, Union
from qdrant_client import QdrantClient
from openai import OpenAI
# from sentence_transformers import SentenceTransformer
# from FlagEmbedding import BGEM3FlagModel

class BaseEmbedding:
    def encode(self, text: str) -> List[float]:
        raise NotImplementedError

# class ParaphraseMiniLMEmbedding(BaseEmbedding):
#     def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
#         self.model = SentenceTransformer(model_name)

#     def encode(self, text: str) -> List[float]:
#         return self.model.encode(text, convert_to_numpy=True).tolist()

# class BGEEmbedding(BaseEmbedding):
#     def __init__(self, model_name: str, use_fp16: bool = True):
#         self.model = BGEM3FlagModel(model_name, use_fp16=use_fp16)

    # def encode(self, text: str) -> List[float]:
    #     emb = self.model.encode(text, return_dense=True)
    #     return emb["dense_vecs"]
class OpenAIEmbedding(BaseEmbedding):
    def __init__(self, model_name: str):
        self.client = OpenAI()
        self.model_name = model_name
    def encode(self, text: str) -> List[float]:
        return self.client.embeddings.create(
            model=self.model_name, 
            input=text
        ).data[0].embedding

class QdrantSearch:
    def __init__(self, host: str, collection_name: str, embedder: BaseEmbedding):
        self.client = QdrantClient(host)
        self.collection_name = collection_name
        self.embedder = embedder

    def search(
        self, query_text: str, limit: int = 20, return_full: bool = True
    ) -> Union[List[int], List[Dict]]:
        dense_vec = self.embedder.encode(query_text)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=dense_vec,
            limit=limit,
            with_payload=True
        )

        if return_full:
            return [
                {
                    "cid": point.payload["cid"],
                    "text": point.payload["text"],
                    "score": point.score
                }
                for point in results
            ]
        else:
            return [point.payload["cid"] for point in results]