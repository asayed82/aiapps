
from typing import Any
import os
import logging
from google.cloud import storage
import trafilatura as trafi
from lxml import etree
from langchain.document_loaders import (
        PyPDFLoader,
        DirectoryLoader,
        UnstructuredHTMLLoader,
        GCSFileLoader,
        GCSDirectoryLoader
    )

from utils import consts, config


logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_gcs_files(bucket_name: str, file_type:str=consts.DocType.PDF.value) -> list[Any]:

    #storage_client = storage.Client()
    #blobs = storage_client.list_blobs(bucket_name, max_results=max_results, prefix=folder_name)

    loader_cls=PyPDFLoader
    if file_type == consts.DocType.HTML.value:
        loader_cls = UnstructuredHTMLLoader

    loader = GCSDirectoryLoader(project_name=config.GCP_PROJECT_ID, bucket=bucket_name, loader_func=loader_cls)

    docs = loader.load() 

    print("# of docs loaded = %i",  len(docs))

    return docs

def load_local_files(local_dir_path: str = None, file_type:str=consts.DocType.PDF.value) -> list:
    logger.info("loading docs...")

    loader = None
    if not local_dir_path:
        raise ValueError("a dir path or doc path has to be specified")
    
    loader_cls=PyPDFLoader
    if file_type == consts.DocType.HTML.value:
        loader_cls = UnstructuredHTMLLoader
    
    loader = DirectoryLoader(local_dir_path, loader_cls=loader_cls)

    docs = loader.load() 

    print("# of docs loaded = %i",  len(docs))

    return docs

def get_files_in_dir(dir_path:str):
    for file in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file)):
            yield file

def clean_html_content(html_content):
    html_str = None

    print(f"Cleaning HTML content: {html_content}")

    try:
        html_str = trafi.bare_extraction(
            filecontent=html_content,
            output_format="xml",
            include_formatting=False,
            include_comments=True,
            include_tables=True,
            include_links=False,
            include_images=False,
            favor_recall=True,
            target_language="en",
        )
        
    except Exception as e:
        logging.warning("Couldn't parse content: %s", e)
        return html_str
    
    print(f"Cleaned HTML content: {html_str}")
    
    main_content = "<html><head><title>" + str(html_str["title"]) + "</title></head>" + str(etree.tostring(html_str["body"])) + "</html>" 
    #main_content = str(html_str)
    main_content = str.replace(main_content, "b'<body>", "<body>")
    main_content = str.replace(main_content, "<body>", "<body><h1>" + str(html_str["title"]) + "</h1>" )
    main_content = str.replace(main_content, "</body>'", "</body>")  
    main_content = str.replace(main_content, "<row>", "<tr>") 
    main_content = str.replace(main_content, "</row>", "</tr>") 
    main_content = str.replace(main_content, "<cell>", "<td>") 
    main_content = str.replace(main_content, "</cell>", "</td>") 

    return main_content