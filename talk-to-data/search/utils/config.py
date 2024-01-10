from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #GCP Settings
    project_id:str = ""
    location:str = "us-central1"
    port:int=8080


    #VDB Connection Settings
    db_instance:str="genai-pg"
    db_name:str="search"
    db_host:str=""
    db_port:str="5432"
    db_user:str="postgres"
    db_password:str="passw0rd"


    #Documents Only settings
    docs_bucket:str =""
    doc_collection:str=""

    #Videos Only settings
    videos_bucket:str = ""
    clips_bucket:str = ""
    video_table:str="videos"
    video_collection:str="videos_col"
    min_video_clip_duration_secs:int=30
    max_video_clip_duration_secs:int=60