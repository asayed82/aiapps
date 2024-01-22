import time, asyncio, math, json
import multiprocessing
from utils import doc_process, consts
from utils import config

settings = config.Settings()

TASK_INDEX = settings.cloud_run_task_index
TASK_COUNT = settings.cloud_run_task_count


def doc_process_callback():
    global processed_count
    processed_count += 1
    print(f"{processed_count} docs processed")


def multiprocessdocs(docs, callback):
    processor = doc_process.Client(settings=settings)
    for doc in docs:
        processor.process_doc_lc(doc, callback)

    processor.engine.dispose()

pd_keys = {
    'title_en': 'title',
    'brand_code': 'brand',
    'comcat_2': 'commercial category',
    'product_subtype': 'category',
    'colour_family': 'colour',
    'offer_price': 'price',
    'instock_flag': 'is stock available ?',
    'deal_flag': 'is it on deal ?',
    'seller_rating': 'seller rating',
    'is_returnable': 'is returnable ?',
    'product_rating': 'product rating',
    'image_url': 'image url',
    'product_url': 'product url',
    'is_locker_eligible': 'is eligible for locker ?',
    'bnpl_flag': 'is available on emi ?'
}


def process_process_pd_key(key):
    return pd_keys.get(key) or key


def process_process_pd_value(key, value):
    try:
        if key in ('instock_flag', 'deal_flag', 'is_returnable', 'is_locker_eligible', 'bnpl_flag'):
            value = value or 0
            if int(value) == 1:
                return "yes"
            return "no"
        if key == 'discount':
            value = value or 0
            return round(float(value)*100, 2)
    except:
        return value

    return value


def process_specs(specs):
    specs = json.loads(specs) if specs else ''
    return ". ".join([f"{spec['name']} {spec['value']}" for spec in specs])


def preprocess_docs(docs):
    for doc in docs:
        product_detail = json.loads(doc.page_content.lower())
        if not product_detail.get('title_en'):
            return
        title = product_detail['title_en']
        noon_details = ". ".join([process_process_pd_key(y) + ' ' + str(process_process_pd_value(y, product_detail[y])) for y in product_detail if y not in ('description', 'highlights', 'specifications', 'sku_config', 'offer_code')])
        specs = f"specifications for {title} are {process_specs(product_detail.get('specifications'))}"
        highlights = f"highlights for {title} are {product_detail.get('highlights')}"
        description = f"description for {title} are {product_detail.get('description')}"
        new_page_content = f"{noon_details} . {specs} . {description} . {highlights}"
        print(new_page_content)
        doc.page_content = new_page_content


def process():
    print(
        f"Task {TASK_INDEX}: Processing part {TASK_INDEX} of {TASK_COUNT} "
        f"with following settings {settings.model_dump()}")

    method_start = time.time()

    if settings.file_type in [consts.FileType.HTML.value, consts.FileType.PDF.value]:

        processor = doc_process.Client(settings=settings)

        docs = processor.dl.load_gcs_docs_to_lc(bucket_name=processor.docs_bucket, file_type=processor.file_type)

        print(f"******* {len(docs)} documents to be processed...")
        counter = multiprocessing.Value('i', 0)
        with multiprocessing.Pool() as pool:
            pool.starmap(processor.process_doc_lc, [(doc, counter) for doc in docs])
        print(f"Doc {counter.value}/{len(docs)} processed")

    elif settings.file_type == consts.FileType.JSON.value:
        processor = doc_process.Client(settings=settings)
        docs = processor.dl.load_gcs_file_to_lc(bucket_name=processor.docs_bucket,
                                                blob_name='noon-catalog-data/Chatbot_data_filtered.json')
        preprocess_docs(docs)
        print(f"******* {len(docs)} documents to be processed...")
        # batches = []
        # i = 0
        # batch_size = 1000
        # while i < len(docs):
        #     batches.append([i, i+batch_size])
        #     i += batch_size
        # print(batches)
        # with multiprocessing.Pool() as pool:
        #     pool.starmap(multiprocessdocs, [(docs[b[0]: b[1]], doc_process_callback) for b in batches])

        batch_size = math.ceil(len(docs) / TASK_COUNT)
        batch_start_idx = batch_size * TASK_INDEX
        batch_docs = docs[batch_start_idx: batch_start_idx + batch_size]

        for idx, doc in enumerate(batch_docs):
            print(f"=====Processing doc {idx + 1}/{len(batch_docs)} - Task: {TASK_INDEX}")
            processor.process_doc_lc(doc, doc_process_callback)

    else:
        raise ValueError(f"File type {settings.file_type} not supported")

    time_taken = round(time.time() - method_start, 3)

    print(f"Job Processed in {time_taken}s ")


if __name__ == "__main__":
    process()
