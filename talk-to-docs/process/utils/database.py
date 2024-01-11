from langchain.vectorstores.pgvector import PGVector
from utils import config

class Client:
    def __init__(self, settings: config.Settings) -> None:
        self.project_id = settings.project_id
        self.location = settings.location
        self.db_instance = settings.db_instance
        self.db_name = settings.db_name
        self.db_host = settings.db_host
        self.db_port = settings.db_port
        self.db_user = settings.db_user
        self.db_password = settings.db_password
        self.db_doc_collection = settings.doc_collection

    def get_lc_pgv_connection_string(self):
        return PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )

    async def get_connector(self, connector):
        return await connector.connect_async(
            f"{self.project_id}:{self.location}:{self.db_instance}",
            "asyncpg",
            user=f"{self.db_user}",
            password=f"{self.db_password}",
            db=f"{self.db_name}",
        )
