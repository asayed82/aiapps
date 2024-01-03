from dataclasses import dataclass
import os
import streamlit as st
import vertexai
from langchain.chains import LLMChain

# from langchain.llms import vertexai
from langchain.chat_models import ChatVertexAI
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ChatMessageHistory,
    StreamlitChatMessageHistory,
)
from langchain.prompts import PromptTemplate
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain.chains import (
    ConversationalRetrievalChain,
    RetrievalQA,
    StuffDocumentsChain,
)
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import VertexAIEmbeddings

from utils import config, consts, database, embedai


USER = "user"
ASSISTANT = "ai"
MESSAGES = "messages"


GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID") or config.GCP_PROJECT_ID
GCP_LOCATION = os.environ.get("GCP_LOCATION") or config.GCP_LOCATION
DATA_STORE_ID = os.environ.get("DATA_STORE_ID") or config.VAIS_DATASTORE_ID
VAIS_DATASTORE_REGION=os.environ.get("VAIS_DATASTORE_REGION") or config.VAIS_DATASTORE_REGION
PG_INSTANCE_NAME = os.environ.get("PG_INSTANCE_NAME") or config.PG_INSTANCE_NAME
PG_DATABASE_NAME = os.environ.get("PG_DATABASE_NAME") or config.PG_DATABASE_NAME
PG_DATABASE_USER = os.environ.get("PG_DATABASE_USER") or config.PG_DATABASE_USER
PG_DATABASE_PASSWORD = (
    os.environ.get("PG_DATABASE_PASSWORD") or config.PG_DATABASE_PASSWORD
)
PG_TABLE_NAME = os.environ.get("PG_TABLE_NAME") or config.PG_TABLE_NAME
PG_HOST = os.environ.get("PG_HOST") or config.PG_HOST
PG_PORT = os.environ.get("PG_PORT") or config.PG_PORT
PG_DRIVER = os.environ.get("PG_DRIVER") or config.PG_DRIVER
PG_COLLECTION= os.environ.get("PG_COLLECTION") or config.PG_COLLECTION

# unix_socket_path = os.environ.get("INSTANCE_UNIX_SOCKET") or f'/cloudsql/{GCP_PROJECT_ID}:{GCP_LOCATION}:{PG_INSTANCE_NAME}'

vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)

history = StreamlitChatMessageHistory(key="st_history_key")


@dataclass
class Message:
    actor: str
    payload: str


@st.cache_resource
def get_llm() -> ChatVertexAI:
    return ChatVertexAI(
        model_name="chat-bison@002",
        max_output_tokens=2000,
        temperature=0,
        top_p=0.8,
        top_k=1,
        verbose=True,
    )


@st.cache_resource
def get_custom_db() -> database.Client:
    return database.Client(
        gcp_project_id=GCP_PROJECT_ID,
        gcp_location=GCP_LOCATION,
        pg_instance_name=PG_INSTANCE_NAME,
        pg_database_user=PG_DATABASE_USER,
        pg_database_password=PG_DATABASE_PASSWORD,
        pg_database_name=PG_DATABASE_NAME,
    )


# @st.cache_resource
def get_std_db() -> PGVector:
    CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver=PG_DRIVER,
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DATABASE_NAME,
        user=PG_DATABASE_USER,
        password=PG_DATABASE_PASSWORD,
    )
    return PGVector(
        collection_name=PG_COLLECTION,
        connection_string=CONNECTION_STRING,
        embedding_function=VertexAIEmbeddings(
            model_name=consts.VAIModelName.TXT_EMBED.value
        ),
    )


async def match_similar_docs_from_db(text_query: str):
    query_embed = embedai.get_txt_embedding(
        text=text_query, task_type=consts.EmbeddingTaskType.RETRIEVAL_QUERY.value
    )[0]

    matches = await get_custom_db().list_similar_docs(
        query_embed=query_embed, sim_thres=float(0.5), num_matches=int(5)
    )

    results = []

    for ma in matches:
        results.append({"page_content": ma["page_content"], "doc_link": ma["doc_link"]})

    return results


def get_llm_chain_w_customsearch():
    condense_question_template = """

        Return text in the original language of the follow up question.
        Never rephrase the follow up question given the chat history unless the follow up question needs context.
        
        Chat History: {chat_history}
        Follow Up question: {question}
        Standalone question:
    """
    condense_question_prompt = PromptTemplate.from_template(
        template=condense_question_template
    )

    combine_prompt = PromptTemplate(
        template="""Use the following pieces of context and chat history to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Context: {context}
        Chat history: {chat_history}
        Question: {question} 
        Helpful Answer:""",
        input_variables=["context", "question", "chat_history"],
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        output_key="answer",
        human_prefix=USER,
        ai_prefix=ASSISTANT,
        return_messages=True,
        chat_memory=history,
    )

    retriever = None
    if DATA_STORE_ID:

        retriever = GoogleVertexAISearchRetriever(
            project_id=GCP_PROJECT_ID,
            location_id=VAIS_DATASTORE_REGION,
            data_store_id=DATA_STORE_ID,
            max_documents=5,
            engine_data_type=0,
            
        )
    else:
        retriever = get_std_db().as_retriever(
            search_type=consts.SearchType.SIMILARITY.value,
            search_kwargs={"score_threshold": 0.1, "k": 3},
        )
        
    conversation = ConversationalRetrievalChain.from_llm(
            llm=get_llm(),
            retriever=retriever,
            verbose=True,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": combine_prompt},
            chain_type=consts.ChainMethod.STUFF.value,
            rephrase_question=False,
            condense_question_prompt=condense_question_prompt,
            condense_question_llm=get_llm(),
            return_source_documents=True,
        )

    return conversation


def initialize_session_state():
    if len(history.messages) == 0:
        history.add_ai_message("Hi there! How can I help you?")

    if "llm_chain" not in st.session_state:
        st.session_state["llm_chain"] = get_llm_chain_w_customsearch()


def get_llm_chain_from_session() -> LLMChain:
    return st.session_state["llm_chain"]


initialize_session_state()

msg: Message
for msg in history.messages:
    st.chat_message(msg.type).write(msg.content)

prompt: str = st.chat_input("Enter a prompt here")

if prompt:
    # history.add_user_message(prompt)
    st.chat_message(USER).write(prompt)

    with st.spinner("Please wait.."):
        print(f"YOUR PROMPT={prompt}")
        llm_chain = get_llm_chain_from_session()
        response: str = llm_chain(
            {"question": prompt, "chat_history": history.messages}
        )["answer"]
        # history.add_ai_message(response)
        st.chat_message(ASSISTANT).write(response)
