import logging
from typing import List
import time
from langchain_community.embeddings import VertexAIEmbeddings
from langchain.pydantic_v1 import BaseModel
from vertexai.preview.language_models import TextEmbeddingInput
from vertexai.language_models import TextEmbeddingModel
from utils import consts
from vertexai.preview.vision_models import MultiModalEmbeddingModel


txt_embed_model = TextEmbeddingModel.from_pretrained(consts.VAIModelName.TXT_EMBED.value)
multimodal_embed_model = MultiModalEmbeddingModel.from_pretrained(consts.VAIModelName.MM_EMBED.value)
lc_vai_embeddings = VertexAIEmbeddings(model_name=consts.VAIModelName.TXT_EMBED.value)


def get_txt_embedding(
    text: str, task_type: str = consts.EmbeddingTaskType.SEMANTIC_SIMILARITY.value
) -> List:
    """Text embedding with a Large Language Model."""
    res = []
    model = TextEmbeddingModel.from_pretrained(consts.VAIModelName.TXT_EMBED.value)
    # embeddings = model.get_embeddings(text_array, )
    embeddings = model.get_embeddings(
        texts=[TextEmbeddingInput(text=text, task_type=task_type)]
    )
    for embedding in embeddings:
        res.append(embedding.values)

    return res


# Embeddings API integrated with langChain
def get_custom_vai_txt_embedding():
    return CustomVertexAIEmbeddings(requests_per_minute=100, num_instances_per_batch=5)

class CustomVertexAIEmbeddings(VertexAIEmbeddings, BaseModel):
    requests_per_minute: int
    num_instances_per_batch: int

    @staticmethod
    def _rate_limit(max_per_minute):
        period = 60 / max_per_minute
        print("Waiting")
        while True:
            before = time.time()
            yield
            after = time.time()
            elapsed = after - before
            sleep_time = max(0, period - elapsed)
            if sleep_time > 0:
                print(".", end="")
                time.sleep(sleep_time)

    # Overriding embed_documents method
    def embed_documents(self, texts: List[str]):
        limiter = self._rate_limit(self.requests_per_minute)
        results = []
        docs = list(texts)
        model = TextEmbeddingModel.from_pretrained(consts.VAIModelName.TXT_EMBED.value)
        #model = self.client

        while docs:
            # Working in batches because the API accepts maximum 5
            # documents per request to get embeddings
            head, docs = (
                docs[: self.num_instances_per_batch],
                docs[self.num_instances_per_batch :],
            )

            inputs = [TextEmbeddingInput(text=doc, task_type=consts.EmbeddingTaskType.RETRIEVAL_DOCUMENT.name) for doc in head]

            chunk = model.get_embeddings(inputs)
            results.extend(chunk)
            next(limiter)

        return [r.values for r in results]
