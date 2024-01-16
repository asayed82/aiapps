from utils import consts
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    #GCP Settings
    project_id: str = "noondev-chatbot"
    location: str = "us-east1"
    file_type: str = consts.FileType.JSON.value

    #JOB Settings
    cloud_run_task_index: int = 0
    cloud_run_task_count: int = 1

    #VDB Connection Settings
    db_instance: str = "my_instance"
    db_name: str = "postgres"
    db_host: str = ""
    db_port: int = 5432
    db_user: str = "rmundhada"
    db_password: str = "postgres"

    #Documents Only settings
    docs_bucket: str = "noongpt_training_data"
    doc_collection: str = "noon_catalog_openai3"
    doc_processing_batch_size: int = 5
