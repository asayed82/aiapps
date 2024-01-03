import asyncio
import asyncpg
import logging
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from utils import config


logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Client:
    def __init__(self, gcp_project_id, gcp_location, pg_instance_name, pg_database_user, pg_database_password, pg_database_name) -> None:
            self.gcp_project_id = gcp_project_id
            self.gcp_location = gcp_location
            self.pg_instance_name = pg_instance_name
            self.pg_database_user = pg_database_user
            self.pg_database_password = pg_database_password
            self.pg_database_name = pg_database_name


    async def get_connector(self, connector):

        return await connector.connect_async(
                f"{self.gcp_project_id}:{self.gcp_location}:{self.pg_instance_name}",
                "asyncpg",
                user=f"{self.pg_database_user}",
                password=f"{self.pg_database_password}",
                db=f"{self.pg_database_name}",
            )


   
    async def list_similar_docs(self, query_embed, sim_thres:float, num_matches:int):

        matches=[]
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await self.get_connector(connector)

            await register_vector(conn)

            # Store all the generated embeddings back into the database.
            results = await conn.fetch(
                    f""" SELECT doc_id, doc_link, doc_name,doc_content, start_index, 1-(embedding <=>$1) AS similarity
                    FROM {config.PG_TABLE_NAME}
                    WHERE 1-(embedding <=>$1) > $2
                    ORDER BY similarity DESC
                    LIMIT $3
                    """,
                    query_embed, sim_thres, num_matches

                )
            if len(results) == 0:
                print("Did not find any results. Adjust the query parameters.")

            for r in results:
                matches.append({
                    "doc_id": r["doc_id"],
                    "doc_link": r["doc_link"],
                    "doc_name": r["doc_name"],
                    "doc_content": r["doc_content"],
                    "start_index": r["start_index"],
                    "similarity": r["similarity"]
                })
            print("Query completed...")
            await conn.close()
        return matches


