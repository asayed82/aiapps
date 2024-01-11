import time
from utils import video_process, consts, config

settings = config.Settings()


def initialise():
    print(
        f"Initialization started with the following settings {settings.model_dump()}"
        )

    method_start = time.time()
    
    processor = video_process.Client(settings=settings)
    
    processor.create_video_tables()

    time_taken = round(time.time() - method_start, 3)

    print(f"Job init completed in {time_taken}s ")


if __name__ == "__main__":
    initialise()
