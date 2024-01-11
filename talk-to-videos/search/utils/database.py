import asyncio, asyncpg
from langchain.vectorstores.pgvector import PGVector
from google.cloud.sql.connector import Connector
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
        self.video_collection = settings.video_collection
        self.video_table = settings.video_table


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
    
    async def list_videos(self, video_ids:tuple):

        matches=[]
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await self.get_connector(connector)

            # Store all the generated embeddings back into the database.
            results = await conn.fetch(
                    f""" SELECT video_id, video_name, video_src, video_title, video_labels, video_desc, video_duration
                        FROM {self.video_table}
                        WHERE video_id in {str(video_ids)}
                    """,
                )
            if len(results) == 0:
                print("Did not find any related video ids")

            for r in results:
                matches.append({
                    "video_id": r["video_id"],
                    "video_name": r["video_name"],
                    "video_src": r["video_src"],
                    "video_title": r["video_title"],
                    "video_labels": r["video_labels"],
                    "video_desc": r["video_desc"],
                    "video_duration": r["video_duration"],
                })
            print("Video Query completed...")
            await conn.close()
        return matches

