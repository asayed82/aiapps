import asyncio
import asyncpg
import logging
import numpy as np
import pandas as pd
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from langchain.vectorstores.pgvector import PGVector
from utils import config


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        self.db_doc_collection = settings.db_doc_collection
        self.db_video_table = settings.db_video_table
        self.db_video_segs_table = settings.db_video_segs_table
        self.db_video_collection = settings.db_video_collection

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


    async def create_video_segs_table(self):
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await self.get_connector(connector)

            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)

            # Create the `video_embeddings` table.
            await conn.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.db_video_segs_table}(
                                            video_id INTEGER,
                                            index INTEGER,
                                            start_secs FLOAT,
                                            end_secs FLOAT,
                                            duration FLOAT,
                                            transcript VARCHAR(10000),
                                            description VARCHAR(10000),
                                            labels VARCHAR(1000),
                                            embedding vector(768))"""
            )
            print("Create Video Segments Table Done...")
            await conn.close()

    async def create_video_table(self):
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await self.get_connector(connector)

            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)

            # Create the `video_embeddings` table.
            await conn.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.db_video_table}(
                                            video_id SERIAL PRIMARY KEY,
                                            video_name VARCHAR(100),
                                            video_link VARCHAR(1000),
                                            video_title VARCHAR(1000),
                                            video_labels VARCHAR(1000),
                                            video_desc VARCHAR(1000),
                                            video_duration FLOAT)
                                            """
            )
            print("Create Video Table Done...")
            await conn.close()

    async def insert_video_segment(self, df: pd.DataFrame):
        if type(df["embedding"][0]) == list:
            df["embedding"] = df["embedding"].apply(lambda x: np.array(x))
        elif type(df["embedding"][0]) == str:
            df["embedding"] = df["embedding"].apply(
                lambda x: np.array(x.strip("][").split(","))
            )
        else:
            pass
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await self.get_connector(connector)

            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)
            # Store all the generated embeddings back into the database.
            for _, row in df.iterrows():
                await conn.execute(
                    f"INSERT INTO {self.db_video_segs_table} (video_id, index, start_secs, end_secs, duration, transcript, description, labels, embedding) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
                    row["video_id"],
                    row["index"],
                    row["start_secs"],
                    row["end_secs"],
                    row["duration"],
                    row["transcript"],
                    row["description"],
                    row["labels"],
                    row["embedding"],
                )
            print("Insert Video Segments Done...")
            await conn.close()

    async def insert_video(self, video_row:dict) -> int:

        video_id = None

        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await self.get_connector(connector)

            video_id = await conn.fetchval(f"INSERT INTO {self.db_video_table} (video_link, video_name, video_title, video_labels, video_desc, video_duration) VALUES ($1, $2, $3, $4, $5, $6) RETURNING video_id" ,
                        video_row["video_link"], video_row["video_name"], video_row["video_title"], video_row["video_labels"], video_row["video_desc"], video_row["video_duration"]
                    )
            print(f"Insert Video Done with ID ={video_id}")

            await conn.close()

        return video_id