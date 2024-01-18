from utils import consts
from pydantic_settings import BaseSettings


def get_openai_api_key():
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/noondev-chatbot/secrets/OPENAI_API_KEY/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')


#llms keys
openai_api_key = get_openai_api_key()

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
