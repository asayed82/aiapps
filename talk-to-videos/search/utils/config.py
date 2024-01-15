from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #GCP Settings
    project_id:str = ""
    location:str = "us-central1"
    port:int=8080


    #VDB Connection Settings
    db_instance:str="genai-pg"
    db_name:str="doc_search"
    db_host:str=""
    db_port:str="5432"
    db_user:str="postgres"
    db_password:str="postgres"


    #Videos Only settings
    clips_bucket:str ="video-sample-clips"
    video_table:str="sample_videos"
    video_segs_table:str="sample_videos_segs"
    video_collection:str="sample_videos_col"

