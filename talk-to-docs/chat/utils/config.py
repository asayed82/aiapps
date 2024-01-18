from utils import consts
from pydantic_settings import BaseSettings


def get_secret(secret_key):
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/noondev-chatbot/secrets/{secret_key}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')


openai_api_key = get_secret('OPENAI_API_KEY')
db_pwd = get_secret('POSTGRES_PASSWORD')


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
    db_instance: str = "noongpt"
    db_name: str = "postgres"
    db_host: str = "34.75.73.98"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = db_pwd


    #Documents Retriever settings
    doc_collection: str = "openai_collection"
