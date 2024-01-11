import datetime
import os
import ffmpeg
from utils import data_loader, visionai, config

settings = config.Settings()

dl = data_loader.Client(settings=settings)

def preprocess_all_videos():

    video_names = dl.load_gcs_files(bucket_name=dl.videos_bucket)

    print(f"{len(video_names)} videos to preprocess...")
    
    for name in video_names:
        split_video_into_clips(dl.videos_bucket, dl.clips_bucket, name)


def split_video_into_clips(videos_bucket: str, clips_bucket:str, video_name: str):

    video_uri = f"gs://{videos_bucket}/{video_name}"

    print(f'========Processing video : "{video_uri}"')

    video_tmp_path = f"tmp/{video_name}"
    dl.download_gcs_to_local(bucket_name=videos_bucket, blob_name=video_name, file_path=video_tmp_path)

    clips, _ = visionai.parse_video_shots(visionai.extract_video_shots(video_uri=video_uri))

    print(f"initial # of clips ={len(clips)}")

    merged_clips = visionai.merge_intervals(clips, settings.min_video_clip_duration_secs, settings.max_video_clip_duration_secs)

    print(f"merged # of clips ={len(merged_clips)}")

    for i, clip in enumerate(merged_clips):

        video_clip_name = f"clip_{i}_{video_name}"

        print(f"-----Creating clip for {video_clip_name}...")

        video_clip_tmp_path = str.replace(video_tmp_path, video_name, video_clip_name)

        video_subclip(input_video_path=video_tmp_path, output_video_path=video_clip_tmp_path, start_second=clip["start_secs"], end_second=clip["end_secs"])
    
        dl.upload_local_to_gcs(file_path=video_clip_tmp_path, bucket_name=clips_bucket, blob_name=video_clip_name)

        os.remove(video_clip_tmp_path)

    os.remove(video_tmp_path)


def video_subclip(input_video_path: str, output_video_path:str, start_second: float, end_second: float):
    
    ffmpeg.input(
        input_video_path,
        ss=str(datetime.timedelta(seconds=start_second)),
        to=str(datetime.timedelta(seconds=end_second)),
    ).output(output_video_path, loglevel="quiet").run()

if __name__== "__main__":

    preprocess_all_videos()

