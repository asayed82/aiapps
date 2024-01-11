import time, asyncio, math
from utils import video_process
from utils import config

settings = config.Settings()

TASK_INDEX = settings.cloud_run_task_index
TASK_COUNT = settings.cloud_run_task_count


def process():

    print(
        f"Task {TASK_INDEX}: Processing part {TASK_INDEX} of {TASK_COUNT} "
        f"with following settings {settings.model_dump()}")

    method_start = time.time()
    
    processor = video_process.Client(settings=settings)

    video_names = processor.dl.load_gcs_files(bucket_name=processor.dl.clips_bucket)

    print(f"******* {len(video_names)} videos to be processed...")

    batch_size = math.ceil(len(video_names)/TASK_COUNT)
    batch_start_idx = batch_size*TASK_INDEX
    batch_videos = video_names[batch_start_idx: batch_start_idx + batch_size]

    for idx, name in enumerate(batch_videos):

        print(f"=====Processing video {idx+1}/{len(batch_videos)}: {name} - Task: {TASK_INDEX}")

        asyncio.run(processor.process_video_from_gcs(bucket_name=processor.dl.clips_bucket, video_name=name))

    time_taken = round(time.time() - method_start, 3)

    print(f"Job Processed in {time_taken}s ")

if __name__ == "__main__":
    process()