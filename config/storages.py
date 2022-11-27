from storages.backends.s3boto3 import S3Boto3Storage

class S3DefaultStorage(S3Boto3Storage):
    location = "media"

class S3StaticStorage(S3Boto3Storage):
    location = "static"
