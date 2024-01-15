
import os
from google.cloud import storage
from utils import config

class Client:
    def __init__(self, settings: config.Settings) -> None:
        self.project_id = settings.project_id
        self.location = settings.location
        self.videos_bucket = settings.videos_bucket
        self.clips_bucket = settings.clips_bucket

    
    def load_gcs_files(self, bucket_name:str, content_type:str, max_results: int = None) -> list[str]:
        storage_client = storage.Client()

        file_names = []

        blobs = storage_client.list_blobs(bucket_name, max_results=max_results)

        for blob in blobs:
            if blob.content_type != content_type:
                print(
                    f"Skipping non-supported file: {blob.name} - Mimetype: {blob.content_type}"
                )
                continue
            file_names.append(blob.name)

        return file_names


    def delete_gcs_blob(self, bucket_name, blob_name):
        """Deletes a blob from the bucket."""


        storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        generation_match_precondition = None


        blob.reload() 
        generation_match_precondition = blob.generation

        blob.delete(if_generation_match=generation_match_precondition)

    def download_gcs_to_local(
        self, bucket_name: str, blob_name: str, file_path: str
    ):
        storage.Client(project=self.project_id).bucket(bucket_name).blob(
            blob_name
        ).download_to_filename(file_path)

    def upload_local_to_gcs(
        self,
        file_path: str,
        bucket_name: str,
        blob_name: str,
    ):
        storage.Client(project=self.project_id).bucket(bucket_name).blob(
            blob_name
        ).upload_from_filename(file_path)

    def get_files_in_dir(self, dir_path: str):
        for file in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file)):
                yield file
