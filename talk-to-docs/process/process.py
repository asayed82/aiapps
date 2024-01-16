import time, asyncio, math
from utils import doc_process, consts
from utils import config

settings = config.Settings()

TASK_INDEX = settings.cloud_run_task_index
TASK_COUNT = settings.cloud_run_task_count


def process():

    print(
        f"Task {TASK_INDEX}: Processing part {TASK_INDEX} of {TASK_COUNT} "
        f"with following settings {settings.model_dump()}")

    method_start = time.time()

    if settings.file_type in [consts.FileType.HTML.value, consts.FileType.PDF.value]:

        processor = doc_process.Client(settings=settings)

        docs = processor.dl.load_gcs_docs_to_lc(bucket_name=processor.docs_bucket, file_type=processor.file_type)
        
        print(f"******* {len(docs)} documents to be processed...")

        batch_size = math.ceil(len(docs)/TASK_COUNT)
        batch_start_idx = batch_size*TASK_INDEX
        batch_docs = docs[batch_start_idx: batch_start_idx + batch_size]

        for idx, doc in enumerate(batch_docs):

            print(f"=====Processing doc {idx+1}/{len(batch_docs)} - Task: {TASK_INDEX}")
            
            processor.process_doc_lc(doc=doc)
    elif settings.file_type == consts.FileType.JSON.value:
        processor = doc_process.Client(settings=settings)
        docs = processor.dl.load_gcs_file_to_lc(bucket_name=processor.docs_bucket, blob_name='noon-catalog-data/Chatbot_data_filtered.json')

        print(f"******* {len(docs)} documents to be processed...")

        batch_size = math.ceil(len(docs) / TASK_COUNT)
        batch_start_idx = batch_size * TASK_INDEX
        batch_docs = docs[batch_start_idx: batch_start_idx + batch_size]

        for idx, doc in enumerate(batch_docs):
            print(f"=====Processing doc {idx + 1}/{len(batch_docs)} - Task: {TASK_INDEX}")

            processor.process_doc_lc(doc=doc)

    else:
        raise ValueError(f"File type {settings.file_type} not supported")

   
    time_taken = round(time.time() - method_start, 3)

    print(f"Job Processed in {time_taken}s ")

if __name__ == "__main__":
    process()