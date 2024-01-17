from dataclasses import dataclass
import streamlit as st
import vertexai
from langchain.chains import LLMChain

from langchain_community.chat_models import ChatVertexAI, ChatOpenAI
from langchain.memory import (
    ConversationBufferMemory,
    StreamlitChatMessageHistory,
)
from langchain.prompts import PromptTemplate
from langchain_community.retrievers import GoogleVertexAISearchRetriever
from langchain.chains import (
    ConversationalRetrievalChain,
)
from langchain.vectorstores.pgvector import PGVector

from utils import config, consts, database, embedai

settings = config.Settings()

db = database.Client(settings=settings)

vertexai.init(project=settings.project_id, location=settings.location)

history = StreamlitChatMessageHistory(key="st_history_key")

USER = "user"
ASSISTANT = "ai"
MESSAGES = "messages"

@dataclass
class Message:
    actor: str
    payload: str


@st.cache_resource
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model_name="gpt-4", openai_api_key='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')
    # return ChatVertexAI(
    #     model_name="chat-bison@002",
    #     max_output_tokens=2000,
    #     temperature=0,
    #     top_p=0.8,
    #     top_k=1,
    #     verbose=True,
    # )


@st.cache_resource
def get_pgv_db() -> PGVector:
    return PGVector(
        collection_name=settings.doc_collection,
        connection_string=db.get_lc_pgv_connection_string(),
        embedding_function=embedai.openai_embeddings
    )


@st.cache_resource
def get_vais_retriever():
    return  GoogleVertexAISearchRetriever(
            project_id=settings.project_id,
            location_id=settings.location,
            data_store_id=settings.data_store_id,
            max_documents=5,
            engine_data_type=0,
            
        )

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
        template="""Use the following pieces of context and chat history to answer the question at the end.
                    You have to act like expert ecommerce product sales person.
                    Give properly formatted answer wherever possible.
                    Always give answer in bullet points or tabular format to put less congnitive load on user.
                    Give information to user in a way that he is compelled to buy a product.
                    All ways give the full product link to noon.com wherever possible but behind a pretty text.
                    If you don't know the answer, just say that you don't know, don't try to make up an answer.
                    
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
    if settings.data_store_id:
        retriever = get_vais_retriever()
    else:
        retriever = get_pgv_db().as_retriever(
            search_type=consts.SearchType.MMR.value,
            search_kwargs={"score_threshold": 0.1, "k": 5},
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
