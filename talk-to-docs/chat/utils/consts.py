from enum import Enum

class FileType(Enum):
    PDF = "PDF"
    HTML = "HTML"
    CSV = "CSV"
    JSON = "JSON"


class VAIModelName(Enum):
    MULTIMODAL = "gemini-pro-vision"
    TEXT_PALM = "text-bison@002"
    TEXT_GEMINI = "gemini-pro"
    IMAGE = "imagetext@002"
    MM_EMBED = "multimodalembedding@001"
    TXT_EMBED = "textembedding-gecko@003"
    CODE_GENERATE = "code-bison@001"
    CODE_COMPLETE = "code-gecko@001"


class VectorDB(Enum):
    CHROMA = "CHROMA"
    FAISS = "FAISS"
    MATCHING_ENGINE = "MATCHING_ENGINE"


class SearchType(Enum):
    SIMILARITY = "similarity"
    SIMILARITY_THRESHOLD = "similarity_score_threshold"
    MMR = "mmr"

class ChainMethod(Enum):
    STUFF = "stuff"
    MAPREDUCE = "map_reduce"
    REFINE = "refine"

class EmbeddingTaskType(Enum):
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
    RETRIEVAL_QUERY = "RETRIEVAL_QUERY"
    RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT"
    CLASSIFICATION = "CLASSIFICATION"
    CLUSTERING="CLUSTERING"