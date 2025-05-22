import os
from dotenv import load_dotenv
from google.adk.tools import VertexAiSearchTool

load_dotenv()

VAIS_DATASTORE_ID = os.getenv('VAIS_DATASTORE_ID', "projects/my-demo-project-359019/locations/global/collections/default_collection/dataStores/alphabet-finance-pdf_1735976808250")


vertex_search_tool = VertexAiSearchTool(data_store_id=VAIS_DATASTORE_ID)