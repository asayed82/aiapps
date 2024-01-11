from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #GCP Settings
    project_id:str = "my-demo-project-359019"
    location:str = "us-central1"

    #JOB Settings
    cloud_run_task_index:int=0
    cloud_run_task_count:int=1

    #VDB Connection Settings
    db_instance:str="my_instance"
    db_name:str="video_search"
    db_host:str=""
    db_port:str="5432"
    db_user:str="postgres"
    db_password:str="postgres"

    #Videos Only settings
    videos_bucket:str = "my-videos-bucket-name"
    clips_bucket:str = "my-clips-bucket-name"
    db_video_table:str="videos"
    db_video_segs_table:str="videos_segs"
    db_video_collection:str="videos_col"
    min_video_clip_duration_secs:int=30
    max_video_clip_duration_secs:int=60