import time, asyncio, math
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
        docs = processor.dl.load_gcs_file_to_lc(bucket_name=processor.docs_bucket, blob_name='noon-catalog-data/Chatbot_data_filtered.json')

        print(f"******* {len(docs)} documents to be processed...")
        batches = []
        i = 0
        batch_size = 1000
        while i < len(docs):
            batches.append([i, i+batch_size])
            i += batch_size
        print(batches)
        with multiprocessing.Pool() as pool:
            pool.starmap(multiprocessdocs, [(docs[b[0]: b[1]], doc_process_callback) for b in batches])

        # batch_size = math.ceil(len(docs) / TASK_COUNT)
        # batch_start_idx = batch_size * TASK_INDEX
        # batch_docs = docs[batch_start_idx: batch_start_idx + batch_size]
        #
        # for idx, doc in enumerate(batch_docs):
        #     print(f"=====Processing doc {idx + 1}/{len(batch_docs)} - Task: {TASK_INDEX}")
        #
        #     processor.process_doc_lc(doc=doc)

    else:
        raise ValueError(f"File type {settings.file_type} not supported")

   
    time_taken = round(time.time() - method_start, 3)

    print(f"Job Processed in {time_taken}s ")

if __name__ == "__main__":
    process()