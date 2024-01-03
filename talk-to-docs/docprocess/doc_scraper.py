import logging,  os, re
from google.cloud import storage
from bs4 import BeautifulSoup
from lxml import etree, html
import trafilatura as trafi

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


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
    #main_content = str(html_str)
    main_content = str.replace(main_content, "b'<body>", "<body>")
    main_content = str.replace(main_content, "<body>", "<body><h1>" + str(html_str["title"]) + "</h1>" )
    main_content = str.replace(main_content, "</body>'", "</body>")  
    main_content = str.replace(main_content, "<row>", "<tr>") 
    main_content = str.replace(main_content, "</row>", "</tr>") 
    main_content = str.replace(main_content, "<cell>", "<td>") 
    main_content = str.replace(main_content, "</cell>", "</td>") 

    #extract first 10 characters from a string

    norm_title = ''
    if html_str["title"]:
        norm_title = normalise_str(html_str["title"])
        norm_title = norm_title[0:min(100, len(norm_title)-1)]


    return main_content, norm_title


def scrap_docs():

    data_path = os.path.join(os.getcwd(), "data", "noon-all-ds")
    clean_data_path = os.path.join(os.getcwd(), "data", "noon-all-ds-clean")

    html_files = get_files_in_dir(data_path)

    for _, name in enumerate(html_files):

        if name == '.DS_Store':
            continue

        print(f"===Parsin file name {name}")

        html_file = os.path.join(data_path, f"{name}")

        with open(html_file, "r", encoding="utf-8", errors='replace') as f:
            soup = BeautifulSoup(f, 'html.parser')

        html_content = soup.prettify()

        clean_content, title = clean_html_content(html_content)
        html_file_clean = os.path.join(clean_data_path, f"{title}-{name}")
        print(f"Writing clean content to {html_file_clean}")
        with open(html_file_clean, "w", encoding="utf-8") as f:
            f.write(clean_content)


def get_files_in_dir(dir_path:str):
    for file in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file)):
            yield file

def normalise_str(text: str):
   #return ''.join(e for e in text if e.isalnum()).lower().encode('utf8', 'replace').decode('utf8') if text else ""
    return re.sub(" +", "_", re.sub("[^a-zA-Z0-9]", "_", text)).lower()

scrap_docs()