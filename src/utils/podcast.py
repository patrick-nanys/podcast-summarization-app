"""Podcast middleware"""
from fastapi.responses import StreamingResponse
import json
import conf_helper
from middleware import AWS

config = conf_helper.read_configuration()
s3_handler = AWS(config["AWS"]["region"], config["AWS"]["aws_access_key_id"], config["AWS"]["aws_secret_access_key"])

# Podcasts list in S3 bucket
PODCASTS = ["naval_how_to_get_rich", "uranium_mining_outputs"]

def get_podcast_data_by_name(name: str):
    """Get podcast information by name, returns a dict with all values retrieved from s3"""
    if name not in PODCASTS:
        raise Exception("Requested podcast not found in S3.")
    else:
        if name == "naval_how_to_get_rich":
            podcast_name = "How to Get Rich"
            # timestamps json
            podcast_chunks_start_timestamps = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_chunk_start_timestamps.json")
            podcast_chunks_start_timestamps_result = json.loads(podcast_chunks_start_timestamps["Body"].read())
            # json
            podcast_chunks = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_chunks.json")
            json_content_chunks = json.loads(podcast_chunks["Body"].read())
            # mp3
            podcast_mp3_summary = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_read_summary.mp3")
            def iter_mp3_content():
                """Internal function to iterate s3 object content, for mp3 files"""
                for chunk in podcast_mp3_summary["Body"].iter_chunks():
                    yield chunk
            podcast_mp3_summary_result = StreamingResponse(iter_mp3_content(), media_type="audio/mpeg")
            # txt
            podcast_summary_txt = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_summarized_text.json")
            podcast_summary_txt_result = json.loads(podcast_summary_txt["Body"].read())
            # csv
            podcast_transcription_csv = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_transcription.csv")
            def iter_csv_content():
                for chunk in podcast_transcription_csv["Body"].iter_chunks():
                    yield chunk
            podcast_transcription_csv_result = StreamingResponse(iter_csv_content(), media_type="text/csv")
        elif name == "uranium_mining_outputs":
            podcast_name = "How Uranium Mining Works  STUFF YOU SHOULD KNOW"
            # timestamps json
            podcast_chunks_start_timestamps = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_chunk_start_timestamps.json")
            podcast_chunks_start_timestamps_result = json.loads(podcast_chunks_start_timestamps["Body"].read())
            # json
            podcast_chunks = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_chunks.json")
            json_content_chunks = json.loads(podcast_chunks["Body"].read())
            # mp3
            podcast_mp3_summary = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_read_summary.mp3")
            def iter_mp3_content():
                """Internal function to iterate s3 object content, for mp3 files"""
                for chunk in podcast_mp3_summary["Body"].iter_chunks():
                    yield chunk
            podcast_mp3_summary_result = StreamingResponse(iter_mp3_content(), media_type="audio/mpeg")
            # txt
            podcast_summary_txt = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_summarized_text.json")
            podcast_summary_txt_result = json.loads(podcast_summary_txt["Body"].read())
            # csv
            podcast_transcription_csv = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_transcription.csv")
            def iter_csv_content():
                for chunk in podcast_transcription_csv["Body"].iter_chunks():
                    yield chunk
            podcast_transcription_csv_result = StreamingResponse(iter_csv_content(), media_type="text/csv")
    return {
            "Timestamps": podcast_chunks_start_timestamps_result,
            "Chunks": json_content_chunks,
            "MP3": podcast_mp3_summary_result,
            "Summary": podcast_summary_txt_result,
            "CSV":podcast_transcription_csv_result,
        }

