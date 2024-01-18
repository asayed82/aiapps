from typing import Any
import logging
from langchain.docstore.document import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    HTMLHeaderTextSplitter,
    TextSplitter
)
from langchain.vectorstores.pgvector import PGVector
from langchain_community.embeddings import VertexAIEmbeddings
from utils import consts, config, database, data_loader, embedai
from sqlalchemy import create_engine
from sqlalchemy.pool import Pool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Client:
    def __init__(self, settings:config.Settings) -> None:
            
            self.project_id = settings.project_id
            self.location = settings.location
            self.docs_bucket = settings.docs_bucket
            self.file_type = settings.file_type
            self.doc_processing_batch_size= settings.doc_processing_batch_size
            self.db = database.Client(settings=settings)
            self.dl = data_loader.Client(settings=settings)
            self.engine = create_engine(self.db.get_lc_pgv_connection_string(), echo=False, pool_size=15, max_overflow=5, pool_recycle=3600)


    def process_doc_lc(self, doc: Document, callback) -> Any:

        print("-----Processing doc...")

        chunks = self._split_docs(docs=[doc])
        if not chunks:
            return

        CONNECTION_STRING = self.db.get_lc_pgv_connection_string()

        PGVector.from_documents(
            embedding=embedai.lc_vai_embeddings,
            documents=chunks,
            collection_name=self.db.db_doc_collection,
            connection_string=CONNECTION_STRING,
            connection=self.engine
        )

        print(f"seq_num {doc.metadata['seq_num']} processed")

    def _split_docs(self, docs):
        chunk_docs = []
        if self.file_type in (consts.FileType.PDF.value, consts.FileType.JSON.value):
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100, add_start_index=True
            )
            chunk_docs = text_splitter.split_documents(docs)

        elif self.file_type == consts.FileType.HTML.value:
            text_splitter = HTMLHeaderTextSplitter(
                headers_to_split_on=[("h1", "Header1")], return_each_element=True
            )

            for doc in docs:
                chunks = text_splitter.split_text(doc.page_content)
                for chunk in chunks:
                    chunk.metadata = doc.metadata
                    chunk_docs.append(chunk)

        if not chunk_docs or len(chunk_docs) == 0:
            print("NO CHUNK")
            return []
            raise ValueError("Doc splitting resulted in an empty list of chunks")

        print(f"{len(chunk_docs)} chunks obtained after splitting  ")

        return chunk_docs
