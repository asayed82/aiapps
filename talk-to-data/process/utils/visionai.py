
import datetime
import json
from typing import cast, Any
from google.cloud import videointelligence_v1 as vi
from vertexai.preview.generative_models import GenerativeModel, Part
from utils import consts

multimodal_model = GenerativeModel(consts.VAIModelName.MULTIMODAL.value)


def generate_video_description(video_uri: str = None) -> Any:

    
    prompt = """ Describe this video sequence by sequence. The output should be in the following JSON format: \n
                 {"sequences": [{"start_secs": "sequence start in seconds, like 5", "sequence end in seconds, like 10", \n
                                "description": "description of this particular video sequence" }], \n
                 "title": "a title of the entire video", \n
                 "summary": "a brief description of the entire video",\n
                 "labels": "list of labels / tags separated by comma. Not more than 10 labels"}
            """
    
    try:
        video = Part.from_uri(video_uri, mime_type="video/mp4")
        contents = [prompt, video]
        
        response = multimodal_model.generate_content(
            contents, 
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.2,
                "top_p": 0.4,
                "top_k": 8})

        return json.loads(response.text[response.text.index("{"): response.text.rindex("}")+1])
    except Exception:
        return None


def extract_video_seg_content(
    video_uri: str, start_secs: float, end_secs: float
):
    video_client = vi.VideoIntelligenceServiceClient()
    features = [vi.Feature.SPEECH_TRANSCRIPTION, vi.Feature.LABEL_DETECTION]
    detect_config = vi.LabelDetectionConfig(
        label_detection_mode=vi.LabelDetectionMode.LABEL_DETECTION_MODE_UNSPECIFIED
    )
    speech_config = vi.SpeechTranscriptionConfig(
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    segment = vi.types.VideoSegment()
    segment.start_time_offset = datetime.timedelta(seconds=start_secs)
    segment.end_time_offset = datetime.timedelta(seconds=end_secs)

    context = vi.types.VideoContext(
        segments=[segment],
        speech_transcription_config=speech_config,
        label_detection_config=detect_config,
    )

    request = vi.AnnotateVideoRequest(
        input_uri=video_uri, features=features, video_context=context
    )

    operation = video_client.annotate_video(request)

    response = cast(vi.AnnotateVideoResponse, operation.result())

    return response.annotation_results[0]


def parse_video_seg_speech(
    results: vi.VideoAnnotationResults, min_confidence: float = 0.3
) -> str:
    transcriptions = results.speech_transcriptions
    transcriptions = [
        t for t in transcriptions if min_confidence <= t.alternatives[0].confidence
    ]

    result = ""

    for transcription in transcriptions:
        first_alternative = transcription.alternatives[0]
        # confidence = first_alternative.confidence
        transcript = first_alternative.transcript
        result += f" {transcript}"

    return result


def parse_video_seg_labels(
    results: vi.VideoAnnotationResults, min_confidence: float = 0.3
) -> str:
    segment_labels = results.segment_label_annotations

    labels = set()

    for _, segment_label in enumerate(segment_labels):
        for _, segment in enumerate(segment_label.segments):
            confidence = segment.confidence
            if confidence > min_confidence:
                labels.add(segment_label.entity.description)

    return ", ".join(labels)


def extract_video_shots(video_uri: str):
    video_client = vi.VideoIntelligenceServiceClient()
    features = [vi.Feature.SHOT_CHANGE_DETECTION]

    request = vi.AnnotateVideoRequest(input_uri=video_uri, features=features)

    operation = video_client.annotate_video(request=request)

    # Wait for operation to complete
    response = cast(vi.AnnotateVideoResponse, operation.result())

    return response.annotation_results[0]


def parse_video_shots(results: vi.VideoAnnotationResults):
    shots = results.shot_annotations

    video_shots = []

    end_secs = 0

    for _, shot in enumerate(shots):
        # t1 = shot.start_time_offset.total_seconds()
        # t2 = shot.end_time_offset.total_seconds()
        start_secs = (
            shot.start_time_offset.seconds + shot.start_time_offset.microseconds / 1e6
        )
        end_secs = (
            shot.end_time_offset.seconds + shot.end_time_offset.microseconds / 1e6
        )

        video_shots.append({"start_secs": start_secs, "end_secs": end_secs})

    return video_shots, end_secs

def merge_intervals(intervals:list[dict], min_seg_duration:int, max_seg_duration:int):

    if not intervals:
        return []

    if len(intervals) == 1:
        return intervals
    
    for index, shot in enumerate(intervals):
            
        cur_duration = shot["end_secs"] - shot["start_secs"]
        if cur_duration >= min_seg_duration and cur_duration <=max_seg_duration:
            continue
        
        if cur_duration > max_seg_duration:
            if  index < len(intervals)-1:
                intervals[index]["end_secs"] = intervals[index]["start_secs"] + max_seg_duration
                intervals[index+1]["start_secs"] = intervals[index]["end_secs"]
                return merge_intervals(intervals, min_seg_duration, max_seg_duration)
        
        elif cur_duration < min_seg_duration:
                if  index < len(intervals)-1:
                    intervals[index]["end_secs"] = intervals[index+1]["end_secs"]
                    intervals.pop(index+1)
                    return merge_intervals(intervals, min_seg_duration, max_seg_duration)
        
        else:
            return intervals
    
          
    return intervals






