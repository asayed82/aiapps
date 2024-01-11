from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #GCP Settings
    project_id:str = ""
    location:str = "us-central1"
    port:int=8080


    #VDB Connection Settings
    db_instance:str="my_instance"
    db_name:str="doc_search"
    db_host:str=""
    db_port:str="5432"
    db_user:str="postgres"
    db_password:str="postgres"


    #Videos Only settings
    clips_bucket:str = "my-bucket-name"
    video_table:str="videos"
    video_segs_table:str="videos_segs"
    video_collection:str="videos_col"