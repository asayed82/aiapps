from typing import Any, List
import logging
import pandas as pd

from langchain.docstore.document import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    HTMLHeaderTextSplitter,
)
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import VertexAIEmbeddings

from utils import consts, database, embedai

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def index_docs_custom(
    docs: List[Document], var: dict, file_type: str = consts.DocType.HTML.value
) -> Any:
    docs = _split_docs(docs=docs, file_type=file_type)

    db = database.Client(
        gcp_project_id=var["gcp_project_id"],
        gcp_location=var["gcp_location"],
        pg_instance_name=var["pg_instance_name"],
        pg_database_user=var["pg_database_user"],
        pg_database_password=var["pg_database_password"],
        pg_database_name=var["pg_database_name"],
    )

    docs_id = []
    doc_link = []
    doc_name = []
    doc_content = []
    start_index = []
    embedding = []

    for i, doc in enumerate(docs):
        print(f"Processing doc {i}...")
        embedding.append(
            embedai.get_txt_embedding(
                text=doc.page_content,
                task_type=consts.EmbeddingTaskType.RETRIEVAL_DOCUMENT.value,
            )[0]
        )
        doc_content.append(doc.page_content)
        doc_link.append(doc.metadata["source"] if "source" in doc.metadata else None)
        doc_name.append(doc.metadata["name"] if "name" in doc.metadata else None)
        docs_id.append(doc.metadata["id"] if "id" in doc.metadata else None)
        start_index.append(
            doc.metadata["start_index"] if "start_index" in doc.metadata else None
        )

        if i >= 20:
            break

    df_merged = pd.DataFrame(
        {
            "doc_id": docs_id,
            "doc_name": doc_name,
            "doc_link": doc_link,
            "doc_content": doc_content,
            "start_index": start_index,
            "embedding": embedding,
        }
    )

    await db.insert_doc(df=df_merged)

    logger.info("Docs indexed")


def index_docs_std(
    docs: List[Document], var: dict, file_type: str = consts.DocType.HTML.value
) -> Any:
    print("Indexing docs...")

    docs = _split_docs(docs=docs, file_type=file_type)

    CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver=var["pg_driver"],
        host=var["pg_host"],
        port=var["pg_port"],
        database=var["pg_database_name"],
        user=var["pg_database_user"],
        password=var["pg_database_password"],
    )

    print(CONNECTION_STRING)

    PGVector.from_documents(
        embedding=VertexAIEmbeddings(model_name=consts.VAIModelName.TXT_EMBED.value),
        documents=docs,
        collection_name=var["pg_collection_name"],
        connection_string=CONNECTION_STRING,
    )

    print("Docs indexed")


def _split_docs(docs, file_type: str):
    if len(docs) < 1:
        logger.error("no docs sent for splitter")

    chunk_docs = []

    if file_type == consts.DocType.PDF.value:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100, add_start_index=True
        )
        chunk_docs = text_splitter.split_documents(docs)

    elif file_type == consts.DocType.HTML.value:
        text_splitter = HTMLHeaderTextSplitter(
            headers_to_split_on=[("h1", "Header1")], return_each_element=True
        )

        for doc in docs:
            chunks = text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                chunk.metadata = doc.metadata
                chunk_docs.append(chunk)

    if not chunk_docs or len(chunk_docs) == 0:
        raise ValueError("Doc splitting resulted in an empty list of chunks")

    print("# of doc chunks = %i", len(chunk_docs))
    print("*" * 79)

    return chunk_docs
