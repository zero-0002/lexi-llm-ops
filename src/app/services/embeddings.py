from openai import OpenAI
from typing import List, Dict, Union
from app.config.settings import cfg_settings
# from sentence_transformers import SentenceTransformer  # COMMENTED FOR OPENAI ONLY

class EmbeddingHandler:
    def __init__(self, provider: str, model_name: str, **kwargs):
        """
        provider: 'openai' (others commented out for now)
        model_name: tên model tương ứng
        kwargs: các tham số bổ sung
        """
        self.provider = provider.lower()
        self.model_name = model_name

        if self.provider == "openai":
            self.client = OpenAI(api_key=cfg_settings.OPENAI_API_KEY)

        # elif self.provider == "sentence-transformers":
        #     self.model = SentenceTransformer(model_name)

        else:
            raise ValueError(f"Provider '{provider}' không được hỗ trợ. Chỉ hỗ trợ 'openai' hiện tại.")

    def encode(
        self,
        texts: Union[str, List[str]],
        return_dense: bool = True,
        return_sparse: bool = False
    ):
        """
        Mô phỏng API của Milvus BGEM3EmbeddingFunction:
        - Trả dict {'dense_vecs': [...], 'sparse_vecs': [...]} tùy tham số
        - texts: string hoặc list string
        """
        if isinstance(texts, str):
            texts = [texts]

        if self.provider == "openai":
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            dense_vecs = [item.embedding for item in response.data]

            result = {}
            if return_dense:
                result['dense_vecs'] = dense_vecs
            if return_sparse:
                result['sparse_vecs'] = None  # OpenAI không trả sparse

            return result

        # elif self.provider == "sentence-transformers":
        #     return self.model.encode(text, convert_to_numpy=True).tolist()

        else:
            raise ValueError(f"Provider '{self.provider}' không được hỗ trợ. Chỉ hỗ trợ 'openai' hiện tại.")