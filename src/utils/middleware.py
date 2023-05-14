""" Middleware script for podcasts manipulation """

import boto3
import os
import logging

from botocore.exceptions import ClientError


class AWS:
    """
    AWS class. Needed for S3 storage handling
    """

    def __init__(self, region: str, key_id: str, access_key: str):
        self.region = region
        self.key_id = key_id
        self.access_key = access_key
        self.client = boto3.client(
            "s3", region_name=self.region, aws_access_key_id=self.key_id, aws_secret_access_key=self.access_key
        )

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
            print(response)
        except ClientError as e:
            logging.error(e)
            return False
        return True
