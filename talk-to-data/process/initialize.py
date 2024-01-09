import time
from utils import video_process, consts, config

settings = config.Settings()

TASK_INDEX = settings.CLOUD_RUN_TASK_INDEX
TASK_COUNT = settings.CLOUD_RUN_TASK_COUNT


def initialise():
    print(
        f"Task {TASK_INDEX}: Processing part {TASK_INDEX} of {TASK_COUNT} "
        f"with following settings {settings.model_dump()}"
    )

    method_start = time.time()

    if settings.file_type in [consts.FileType.HTML.value, consts.FileType.PDF.value]:
        pass

    elif settings.file_type in [consts.FileType.MP4.value]:
        processor = video_process.Client(settings=settings)

        processor.create_video_tables()

    else:
        raise ValueError(f"File type {settings.file_type} not supported")

    time_taken = round(time.time() - method_start, 3)

    print(f"Job init completed in {time_taken}s ")


if __name__ == "__main__":
    initialise()
