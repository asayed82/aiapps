import asyncio
import logging
from flask import Flask, request

from utils import database, doc_indexer, doc_loader, config, consts

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def create_app():
    # Dev only: run "python main.py" and open http://localhost:8080
    
    app = Flask(__name__)

    var={
        "gcp_project_id":config.GCP_PROJECT_ID,
        "gcp_location":config.GCP_LOCATION,
        "gcs_bucket_name": config.GCS_BUCKET_NAME,
        "pg_database_name":config.PG_DATABASE_NAME,
        "pg_instance_name":config.PG_INSTANCE_NAME,
        "pg_host":config.PG_HOST,
        "pg_port":config.PG_PORT,
        "pg_database_user":config.PG_DATABASE_USER,
        "pg_database_password":config.PG_DATABASE_PASSWORD,
        "pg_collection_name":config.PG_COLLECTION_NAME
    }


    @app.post("/process_local_docs")
    async def process_local_docs():
        
        req = request.get_json()
            
        local_dir_path = req["local_dir_path"] if "local_dir_path" in req else config.DATA_LOCAL_PATH
        file_type = req["file_type"] if "file_type" in req else consts.DocType.HTML.value

        print(local_dir_path)
        print(file_type)

        docs = doc_loader.load_local_files(local_dir_path=local_dir_path, file_type=file_type)

        await doc_indexer.index_docs_std(docs=docs, var=var)

        return {"message": "Accepted"}, 202

    @app.post("/process_remote_docs")
    async def process_remote_docs():

        req = request.get_json()
            
        bucket_name = req["bucket_name"] if "bucket_name" in req else config.GCS_BUCKET_NAME
        file_type = req["file_type"] if "file_type" in req else consts.DocType.HTML.value

        print(f" Target blobs of this format: {bucket_name}/*.{file_type}")
    
        docs = doc_loader.load_gcs_files(bucket_name=bucket_name, file_type=file_type)

        await doc_indexer.index_docs_std(docs=docs, var=var)

        return {"message": "Accepted"}, 202

    @app.post("/create_table")
    def create_table():

        db = database.Client(gcp_project_id = config.GCP_PROJECT_ID,
            gcp_location = config.GCP_LOCATION,
            pg_instance_name = config.PG_INSTANCE_NAME,
            pg_database_user = config.PG_DATABASE_USER,
            pg_database_password = config.PG_DATABASE_PASSWORD,
            pg_database_name = config.PG_DATABASE_NAME)

        asyncio.run(db.create_table())

        print("Table Created !")

        return {"message": "Accepted"}, 200

    @app.post("/")
    def index():

        json_data = request.get_json()
        print(json_data)
        msg = json_data["var1"] + " " + json_data["var2"]
        print(msg)

        return {"message": f"{msg}"}, 200
    
    return app


if __name__ == "__main__":
    myapp = create_app()
    myapp.run(host="localhost", port=8080, debug=True)

