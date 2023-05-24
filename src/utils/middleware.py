"""AWS middleware"""
import boto3
import os
import logging
import json

from botocore.exceptions import ClientError


class AWS:
    """
    AWS class. Needed for S3 storage handling
    """

    def __init__(self, region: str, key_id: str, access_key: str):
        self.region = region
        self.key_id = key_id
        self.access_key = access_key
        self.s3 = boto3.resource('s3', region_name=self.region, aws_access_key_id=self.key_id, aws_secret_access_key=self.access_key)
        self.client = boto3.client(
            "s3", region_name=self.region, aws_access_key_id=self.key_id, aws_secret_access_key=self.access_key
        )
        self.session = boto3.Session(aws_access_key_id=self.key_id, aws_secret_access_key=self.access_key)

    def upload_to_bucket(self, filename: str, bucket: str, object_name=None):
        """
        Upload object to bucket.
        """
        if object_name is None:
            object_name = os.path.basename(filename)
        s3 = self.client
        try:
            with open(filename, "rb") as f:
                s3.upload_fileobj(f, bucket, object_name)
            response = s3.list_objects_v2(
                Bucket=bucket,
                MaxKeys=2,
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True
    
    def upload_string_as_file_to_s3(self, bucket_name, key, content):
        # The content is the string you want to write to a new S3 object
        encoded_string = content.encode('utf-8')

        # Create a new S3 object and write the string content to it
        self.s3.Bucket(bucket_name).put_object(Key=key, Body=encoded_string)

    def list_bucket_content(self, bucket: str):
        """
        Read bucket content.
        """
        content = []
        try:
            s3 = self.session.resource('s3')
            bucket = s3.Bucket(bucket)
            for obj in bucket.objects.all():
                content.append(obj.key)
            return json.dumps(content)
        except ClientError as e:
            return f"Some error occured, details: {e}"
        
    def list_podcast_names(self, bucket_name: str, key: str) -> dict[str, str]:
        """
        Read contents of a directory in a bucket
        """
        bucket = self.s3.Bucket(bucket_name)
        names = {}

        for obj in bucket.objects.filter(Prefix=f'{key}/'):
            if obj.key.endswith('config.json'):
                body = obj.get()['Body'].read().decode('utf-8')
                config = json.loads(body)
                folder_name = obj.key.rsplit('/', 2)[1]  # Getting the 'folder' name
                if 'name' in config:
                    names[folder_name] = config['name']

        return names


    def fetch_podcast_from_bucket(self, bucket: str, name: str):
        """
        Get a podcast from the bucket by object key.
        """
        try:
            s3 = self.client
            result = s3.get_object(Bucket=bucket, Key="podcasts/"+name)
            return result
        except ClientError as e:
            return f"Some error occured, details: {e}"
        
    def fetch_audio_file_from_folder(self, bucket: str, key: str):
        response = self.client.list_objects_v2(Bucket=bucket, Prefix=key)
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.mp3'):
                return self.client.get_object(Bucket=bucket, Key=obj['Key'])
            
        raise None

