import os, time
from utils import doc_indexer, doc_loader, config

TASK_INDEX = int(os.environ.get("CLOUD_RUN_TASK_INDEX", 0))
TASK_COUNT = int(os.environ.get("CLOUD_RUN_TASK_COUNT", 1))

var={
        "gcp_project_id":os.environ.get("GCP_PROJECT_ID", config.GCP_PROJECT_ID),
        "gcp_location": os.environ.get("GCP_LOCATION", config.GCP_LOCATION),
        "input_bucket": os.environ.get("INPUT_BUCKET", config.INPUT_BUCKET) ,
        "pg_database_name":os.environ.get("PG_DATABASE_NAME", config.PG_DATABASE_NAME),
        "pg_instance_name":os.environ.get("PG_INSTANCE_NAME", config.PG_INSTANCE_NAME),
        "pg_host":os.environ.get("PG_HOST", config.PG_HOST),
        "pg_port": os.environ.get("PG_PORT", config.PG_PORT),
        "pg_database_user":os.environ.get("PG_DATABASE_USER", config.PG_DATABASE_USER),
        "pg_database_password":os.environ.get("PG_DATABASE_PASSWORD", config.PG_DATABASE_PASSWORD),
        "pg_driver":os.environ.get("PG_DRIVER", config.PG_DRIVER),
        "pg_collection_name":os.environ.get("PG_COLLECTION_NAME", config.PG_COLLECTION_NAME),
        "file_type":os.environ.get("FILE_TYPE", config.FILE_TYPE),
    }

def process():

    print(os.environ.get("TEST", 'DEFAULT_TEST'))

    method_start = time.time()

    print(
        f""" Task {TASK_INDEX}: Processing part {TASK_INDEX} of {TASK_COUNT} for gs://{var["input_bucket"]}"""
    )

    print(f""" Target blobs of this format: {var["input_bucket"]}/*.{var["file_type"]}""")

    docs = doc_loader.load_gcs_files(bucket_name=var["input_bucket"], file_type=var["file_type"])

    doc_indexer.index_docs_std(docs=docs, var=var)

    time_taken = round(time.time() - method_start, 3)

    print(f"Task {TASK_INDEX}: Processed in {time_taken}s ")


if __name__ == "__main__":
    process()