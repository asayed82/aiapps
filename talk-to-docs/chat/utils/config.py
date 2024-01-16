from utils import consts
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #GCP Settings
    project_id: str = "noondev-chatbot"
    location: str = "us-east1"
    file_type: str = consts.FileType.JSON.value
    docs_bucket : str = "noongpt_training_data"

    #Vertex AI Search Settings
    data_store_id : str = ""
    data_store_region : str = ""

    #VDB Connection Settings
    db_instance: str = "my_instance"
    db_name: str = "postgres"
    db_host: str = ""
    db_port: int = 5432
    db_user: str = "rmundhada"
    db_password: str = "postgres"


    #Documents Retriever settings
    doc_collection: str = "noon_catalog_openai3"
