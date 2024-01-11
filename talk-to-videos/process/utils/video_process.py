import asyncio, json
from utils import config, database, embedai, data_loader, visionai
from langchain.vectorstores.pgvector import PGVector
from langchain.docstore.document import Document


class Client:
    def __init__(self, settings:config.Settings) -> None:
            
        self.project_id = settings.project_id
        self.location = settings.location
        self.min_video_clip_duration_secs = settings.min_video_clip_duration_secs
        self.max_video_clip_duration_secs = settings.max_video_clip_duration_secs
        self.db = database.Client(settings=settings)
        self.dl =  data_loader.Client(settings=settings)

    def create_video_tables(self):
         asyncio.run(self.db.create_video_table())

    async def process_video_from_gcs(self, bucket_name:str, video_name:str):

        video_uri = f"gs://{bucket_name}/{video_name}"
        video_url = f"https://storage.googleapis.com/{bucket_name}/{video_name}"

        video_desc = visionai.generate_video_description(f"gs://{bucket_name}/{video_name}")

        if not video_desc or "sequences" not in video_desc:
            raise ValueError(f"Couldn't generate sequences description for video {video_uri}")
    
        
        video_row = {
            "video_src":video_url, 
            "video_name":video_name, 
            "video_title": video_desc["title"],
            "video_labels": video_desc["labels"], 
            "video_desc": video_desc["summary"], 
            "video_duration": float(video_desc["sequences"][-1]["end_secs"])
            }
        
        video_id = await self.db.insert_video(video_row = video_row)

        pgv_connection_str =  self.db.get_lc_pgv_connection_string()


        for idx, seq in enumerate(video_desc["sequences"]):

            print(f"------Analyzing segment {idx+1}/{len(video_desc['sequences'])} of {video_name}------")

            start_sec = float(seq["start_secs"])
            end_sec = float(seq["end_secs"])
            description = seq["description"]

            seg_annotations = visionai.extract_video_seg_content(video_uri=video_uri, start_secs=start_sec, end_secs=end_sec)
            transcript = visionai.parse_video_seg_speech(seg_annotations)
            labels = visionai.parse_video_seg_labels(seg_annotations)

            video_txt_content = json.dumps({"description": description, "transcript": transcript, "labels": labels })

            metadata = {
                "video_id":video_id,
                "segment_index": idx+1,
                "start_sec": start_sec,
                "end_sec": end_sec,
                "duration": float(end_sec - start_sec),
            }

            doc = Document(page_content=video_txt_content, metadata=metadata)
            
            PGVector.from_documents(
                embedding= embedai.lc_vai_embeddings,
                documents=[doc],
                collection_name=self.db.db_video_collection,
                connection_string=pgv_connection_str,
            )

        print(f"Video segments inserted for video {video_name}")