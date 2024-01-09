import time, asyncio, math
from utils import doc_process, video_process, consts
from utils import config

settings = config.Settings()

TASK_INDEX = settings.CLOUD_RUN_TASK_INDEX
TASK_COUNT = settings.CLOUD_RUN_TASK_COUNT


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

    elif settings.file_type in [consts.FileType.MP4.value]:

        processor = video_process.Client(settings=settings)

        video_names = processor.dl.load_gcs_files(bucket_name=processor.dl.clips_bucket)

        print(f"******* {len(video_names)} videos to be processed...")

        batch_size = math.ceil(len(video_names)/TASK_COUNT)
        batch_start_idx = batch_size*TASK_INDEX
        batch_videos = video_names[batch_start_idx: batch_start_idx + batch_size]

        for idx, name in enumerate(batch_videos):

            print(f"=====Processing video {idx+1}/{len(batch_videos)}: {name} - Task: {TASK_INDEX}")

            asyncio.run(processor.process_video_from_gcs(bucket_name=processor.dl.clips_bucket, video_name=name))

    else:
        raise ValueError(f"File type {settings.file_type} not supported")

   
    time_taken = round(time.time() - method_start, 3)

    print(f"Job Processed in {time_taken}s ")

if __name__ == "__main__":
    process()