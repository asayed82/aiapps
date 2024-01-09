from utils import consts
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #GCP Settings
    project_id:str = ""
    location:str = ""
    file_type:str=consts.FileType.HTML.value
    docs_bucket:str =""

    #Vertex AI Search Settings
    data_store_id:str=""
    data_store_region:str=""


    #VDB Connection Settings
    db_instance:str=""
    db_name:str=""
    db_host:str=""
    db_port:str=""
    db_user:str=""
    db_password:str=""


    #Documents Retriever settings
    doc_collection:str=""