import textwrap
import logging
from typing import Any
from langchain.llms import vertexai
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain.chains import RetrievalQA
from utils import config, consts

logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def init_retriever(
    vdb: Any = None,
    vai_data_store_id:str=None,
    search_type: str = consts.SearchType.SIMILARITY.value,
    llm_name: str = consts.VAIModelName.TEXT_PALM.value,
) -> RetrievalQA:
    
    logging.info(msg="initializing retriever....")

    llm = vertexai.VertexAI(
        model_name=llm_name,
        max_output_tokens=256,
        temperature=0,
        top_p=0.8,
        top_k=1,
        verbose=False,
    )

    retriever = None
    if vai_data_store_id:
        retriever = GoogleVertexAISearchRetriever(
                project_id=config.GCP_PROJECT_ID,
                location_id='global',
                data_store_id=vai_data_store_id,
                get_extractive_answers=True,
                max_documents=5,
                max_extractive_answer_count=5,
                engine_data_type=0

        )
    else:
        retriever = vdb.as_retriever(
            search_type=search_type,
            search_kwargs={
                "k": 5,
                "search_distance": 0.6,
                "score_threshold": 0.5,
                "fetch_k": 5,
                "lambda_mult": 0.3,
            },
        )

    logging.info(msg="initialized retriever.")

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type=consts.ChainMethod.STUFF.value,
        retriever=retriever,
        return_source_documents=True,
    )


def query_vdb(retrieval_qa: RetrievalQA, search_query: str):
    result = retrieval_qa({"query": search_query})
    return result
    # return self._formatter(result)


def _formatter(result):
    print(f"Query: {result['query']}")
    print("." * 80)
    if "source_documents" in result.keys():
        for idx, ref in enumerate(result["source_documents"]):
            print("-" * 80)
            print(f"REFERENCE #{idx}")
            print("-" * 80)
            if "score" in ref.metadata:
                print(f"Matching Score: {ref.metadata['score']}")
            if "source" in ref.metadata:
                print(f"Document Source: {ref.metadata['source']}")
            if "document_name" in ref.metadata:
                print(f"Document Name: {ref.metadata['document_name']}")
            print("." * 80)
            print(f"Content: \n{_wrap(ref.page_content)}")
    print("." * 80)
    print(f"Response: {_wrap(result['result'])}")
    print("." * 80)


def _wrap(s):
    return "\n".join(textwrap.wrap(s, width=120, break_long_words=False))
