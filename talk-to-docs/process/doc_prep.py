import logging,  os, re
from bs4 import BeautifulSoup
from lxml import etree
import trafilatura as trafi
from utils import config, data_loader

settings = config.Settings()

dl = data_loader.Client(settings=settings)


def clean_html_content(html_content):
    html_str = None

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
    
    main_content = "<html><head><title>" + str(html_str["title"]) + "</title></head>" + str(etree.tostring(html_str["body"])) + "</html>" 
    main_content = str.replace(main_content, "b'<body>", "<body>")
    main_content = str.replace(main_content, "<body>", "<body><h1>" + str(html_str["title"]) + "</h1>" )
    main_content = str.replace(main_content, "</body>'", "</body>")  
    main_content = str.replace(main_content, "<row>", "<tr>") 
    main_content = str.replace(main_content, "</row>", "</tr>") 
    main_content = str.replace(main_content, "<cell>", "<td>") 
    main_content = str.replace(main_content, "</cell>", "</td>") 


    norm_title = ''
    if html_str["title"]:
        norm_title = normalise_str(html_str["title"])
        norm_title = norm_title[0:min(100, len(norm_title)-1)]


    return main_content, norm_title


def scrap_docs():

    data_path = os.path.join(os.getcwd(), "data", "source")
    clean_data_path = os.path.join(os.getcwd(), "data", "destination")

    html_files = dl.get_files_in_dir(data_path)

    for _, name in enumerate(html_files):

        print(f"===Parsing file name {name}")

        html_file = os.path.join(data_path, f"{name}")

        with open(html_file, "r", encoding="utf-8", errors='replace') as f:
            soup = BeautifulSoup(f, 'html.parser')

        html_content = soup.prettify()

        clean_content, title = clean_html_content(html_content)
        html_file_clean = os.path.join(clean_data_path, f"{title}-{name}")
        print(f"Writing clean content to {html_file_clean}")
        with open(html_file_clean, "w", encoding="utf-8") as f:
            f.write(clean_content)


def scrap_docs_gcs(input_bucket: str, output_bucket:str):

    file_names = dl.load_gcs_files(bucket_name=input_bucket)

    for file_name in file_names:

        file_tmp_path = f"tmp/{file_name}"
        
        dl.download_gcs_to_local(bucket_name=input_bucket, blob_name=file_name, file_path=file_tmp_path)

        with open(file_tmp_path, "r", encoding="utf-8", errors='replace') as f:
            soup = BeautifulSoup(f, 'html.parser')

        html_content = soup.prettify()

        clean_content, _ = clean_html_content(html_content)

        out_file_name = f"clean_{file_name}"

        out_tmp_path = str.replace(file_tmp_path, file_name, out_file_name)

        print(f"Writing clean content to {out_tmp_path}")
        with open(out_tmp_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
    
        dl.upload_local_to_gcs(file_path=out_tmp_path, bucket_name=output_bucket, blob_name=out_file_name)

        os.remove(out_tmp_path)

    os.remove(file_tmp_path)


def normalise_str(text: str):
    return re.sub(" +", "_", re.sub("[^a-zA-Z0-9]", "_", text)).lower()

if __name__ == "__main__":
    scrap_docs_gcs("my-input-bucket", "my-output-bucket")