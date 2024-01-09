from utils import consts
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #GCP Settings
    project_id:str = ""
    location:str = "us-central1"
    file_type:str=consts.FileType.HTML.value

    #JOB Settings
    CLOUD_RUN_TASK_INDEX:int=0
    CLOUD_RUN_TASK_COUNT:int=1

    #VDB Connection Settings
    db_instance:str="genai-pg"
    db_name:str="doc_search"
    db_host:str=""
    db_port:str="5432"
    db_user:str="postgres"
    db_password:str="passw0rd"


    #Documents Only settings
    docs_bucket:str =""
    db_doc_collection:str=""
    doc_processing_batch_size:int=5

    #Videos Only settings
    videos_bucket:str = ""
    clips_bucket:str = ""
    db_video_table:str="videos"
    db_video_segs_table:str="video_segs"
    db_video_collection:str="videos_col"
    min_video_clip_duration_secs:int=30
    max_video_clip_duration_secs:int=60