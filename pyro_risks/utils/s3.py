import boto3

__all__ = ["S3Bucket"]


class S3Bucket:
    """
    A class for manipulating an S3 bucket using Boto3.
    """

    def __init__(self, bucket_name, region_name=None, aws_access_key_id=None, aws_secret_access_key=None):
        """
        Initializes a new instance of the S3Bucket class.

        Args:
            bucket_name (str): The name of the S3 bucket.
            region_name (str): The AWS region where the bucket is located (optional).
            aws_access_key_id (str): The AWS access key ID for the account (optional).
            aws_secret_access_key (str): The AWS secret access key for the account (optional).
        """
        session_args = {}
        if region_name:
            session_args['region_name'] = region_name
        if aws_access_key_id and aws_secret_access_key:
            session_args['aws_access_key_id'] = aws_access_key_id
            session_args['aws_secret_access_key'] = aws_secret_access_key
        self.session = boto3.Session(**session_args)
        self.s3 = self.session.resource('s3')
        self.bucket = self.s3.Bucket(bucket_name)

    def upload_file(self, file_path, object_key):
        """
        Uploads a file to the S3 bucket.

        Args:
            file_path (str): The local path of the file to upload.
            object_key (str): The S3 key (path) where the file will be stored.
        """
        self.bucket.upload_file(file_path, object_key)

    def download_file(self, object_key, file_path):
        """
        Downloads a file from the S3 bucket.

        Args:
            object_key (str): The S3 key (path) of the file to download.
            file_path (str): The local path where the file will be saved.
        """
        self.bucket.download_file(object_key, file_path)

    def delete_file(self, object_key):
        """
        Deletes a file from the S3 bucket.

        Args:
            object_key (str): The S3 key (path) of the file to delete.
        """
        self.bucket.Object(object_key).delete()

    def list_files(self, pattern=None):
        """
        Lists files in the S3 bucket.

        Args:
            pattern (str): The pattern to filter files by (optional).

        Returns:
            A list of file keys (paths) in the bucket.
        """
        files = []
        for obj in self.bucket.objects.all():
            if not pattern or pattern in obj.key:
                files.append(obj.key)
        return files

    def get_file_metadata(self, object_key):
        """
        Retrieves metadata for a file in the S3 bucket.

        Args:
            object_key (str): The S3 key (path) of the file to retrieve metadata for.

        Returns:
            A dictionary containing the metadata for the file.
        """
        obj = self.bucket.Object(object_key)
        metadata = obj.metadata
        return metadata
