import boto3
import json

import os

__all__ = ["S3Bucket"]


class S3Bucket:
    """
    A class for manipulating an S3 bucket using Boto3.

    Example:
        To create an instance of the S3Bucket class with a session, use:

        >>> from pyro_risks.utils.s3 import S3Bucket

        >>> s3 = S3Bucket(
                bucket_name='mybucket',
                endpoint_url='my_endpoint',
                region_name='us-east-1',
                aws_access_key_id='my_access_key_id',
                aws_secret_key='my_secret_key'
            )

        NOTE: credentials should never be in the code.

        To upload a file to the bucket, use:

        >>> s3.upload_file('my_file.txt', 'path/to/my_file.txt')

        To download a file from the bucket, use:

        >>> s3.download_file('path/to/my_file.txt', 'my_downloaded_file.txt')

        To download a folder from the bucket, use:

        >>> s3.download_folder('path/to/my_folder', 'my_downloaded_folder')

        To delete a file from the bucket, use:

        >>> s3.delete_file('path/to/my_file.txt')

        To list files in the bucket, use:

        >>> files = s3.list_files()

        To filter files by a pattern, use:

        >>> pattern_files = s3.list_files(patterns=["pattern1", "pattern2"])

        To get metadata for a file in the bucket, use:

        >>> metadata = s3.get_file_metadata('path/to/my_file.txt')

        To get file size and last modified date for some files in the bucket, use:

        >>> files_metadata = s3.get_files_metadata(prefix="path/to/my_folder_or_file")
    """

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str,
        region_name: str,
        aws_access_key_id: str,
        aws_secret_key: str,
    ) -> None:
        """
        Initializes a new instance of the S3Bucket class.

        Args:
            bucket_name (str): The name of the S3 bucket.
            endpoint_url (str): The AWS endpoint URL.
            region_name (str): The AWS region where the bucket is located.
            aws_access_key_id (str): The AWS access key ID for the account.
            aws_secret_key (str): The AWS secret access key for the account.
        """
        session_args = {}
        if region_name:
            session_args["region_name"] = region_name
        if aws_access_key_id and aws_secret_key:
            session_args["aws_access_key_id"] = aws_access_key_id
            session_args["aws_secret_access_key"] = aws_secret_key
        self.session = boto3.Session(**session_args)
        self.s3 = self.session.resource("s3", endpoint_url=endpoint_url)
        self.bucket = self.s3.Bucket(bucket_name)
        self.bucket_name = bucket_name

    def upload_file(self, file_path: str, object_key: str) -> None:
        """
        Uploads a file to the S3 bucket.

        Args:
            file_path (str): The local path of the file to upload.
            object_key (str): The S3 key (path) where the file will be stored.
        """
        self.bucket.upload_file(file_path, object_key)

    def write_json_to_s3(self, json_data: json, object_key: str) -> None:
        """
        Writes a JSON file on the S3 bucket.

        Args:
            json_data (json): The JSON data we want to upload.
            object_key (str): The S3 key (path) where the file will be stored.
        """
        self.bucket.put_object(
            Key=object_key, Body=bytes(json.dumps(json_data).encode("UTF-8"))
        )

    def download_file(self, object_key: str, file_path: str) -> None:
        """
        Downloads a file from the S3 bucket.

        Args:
            object_key (str): The S3 key (path) of the file to download.
            file_path (str): The local path where the file will be saved.
        """
        self.bucket.download_file(object_key, file_path)

    def download_folder(self, prefix: str, save_path: str = "") -> None:
        """
        Downloads a folder from the S3 bucket.

        Args:
            prefix (str): The S3 key (path) of the folder to download.
            save_path (str, optional): The local folder where the folder tree will be saved.
        """
        if save_path != "" and not (save_path.endswith("/")):
            save_path += "/"
        for obj in self.bucket.objects.filter(Prefix=prefix):
            if not os.path.exists(os.path.dirname(save_path + obj.key)):
                os.makedirs(os.path.dirname(save_path + obj.key))
            self.bucket.download_file(obj.key, save_path + obj.key)

    def delete_file(self, object_key: str) -> None:
        """
        Deletes a file from the S3 bucket.

        Args:
            object_key (str): The S3 key (path) of the file to delete.
        """
        self.bucket.Object(object_key).delete()

    def list_folders(self, prefix: str = "", delimiter: str = "") -> list[str]:
        """
        Lists folders in the S3 bucket.

        Args:
            prefix (str, optional): Only folders with keys starting with this prefix will be listed.
            delimiter (str, optional): The delimiter to use for the folder listing.

        Returns:
            A list of folder keys (paths) in the bucket.
        """
        folders = []
        try:
            for obj in self.bucket.meta.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix, Delimiter=delimiter
            )["CommonPrefixes"]:
                folders.append(obj["Prefix"])
        # If no objects in the bucket match the given prefix and delimiter
        except KeyError:
            pass
        return folders

    def list_files(
        self,
        patterns: list[str] = None,
        prefix: str = "",
        delimiter: str = "",
        limit: int = 0,
    ) -> list[str]:
        """
        Lists files in the S3 bucket.

        Args:
            patterns (list[str], optional): Only files with keys containing one of the patterns will be listed.
            prefix (str, optional): Only folders with keys starting with this prefix will be listed.
            delimiter (str, optional): The delimiter to use for the folder listing.
            limit (int, optional): Limit the number of files in the output list of the function.

        Returns:
            A list of file keys (paths) in the bucket.
        """
        files = []
        object_filter = self.bucket.objects.filter(Prefix=prefix, Delimiter=delimiter)
        if limit != 0: object_filter = object_filter.limit(limit)
        for obj in object_filter:
            if not patterns or (
                type(patterns) == list and any([p in obj.key for p in patterns])
            ):
                files.append(obj.key)
        return files

    def get_file_metadata(self, object_key: str) -> dict:
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

    def get_files_metadata(
        self, patterns: list[str] = None, prefix: str = "", delimiter: str = ""
    ) -> list[dict]:
        """
        Lists files in the S3 bucket with their size in bytes and last modified dates.

        Args:
            patterns (list[str], optional): Only files with keys containing one of the patterns will be listed.
            prefix (str, optional): Only folders with keys starting with this prefix will be listed.
            delimiter (str, optional): The delimiter to use for the folder listing.

        Returns:
            A dictionnary of file keys (paths), file sizes en GB and last modified dates in the bucket.
        """
        files = []
        for obj in self.bucket.objects.filter(Prefix=prefix, Delimiter=delimiter):
            if not patterns or (
                type(patterns) == list and any([p in obj.key for p in patterns])
            ):
                files.append(
                    {
                        "file_name": obj.key,
                        "file_size": round(obj.size * 1.0 / (1024), 2),
                        "file_last_modified": obj.last_modified,
                    }
                )
        return files


def read_credentials(
    credentials_path: str,
) -> dict:
    """
    Retrieves credentials from a file.

    Args:
        credentials_path (str): The path of the file containing the credentials.

    Returns:
        A dictionary containing the credentials for aws s3 access.
    """
    credentials = {}
    with open(credentials_path + "credentials", "r") as f:
        lines = f.readlines()
        for line in lines:
            if "aws_access_key_id" in line:
                credentials["aws_access_key_id"] = line.split("=")[1].strip()
            if "aws_secret_access_key" in line:
                credentials["aws_secret_key"] = line.split("=")[1].strip()

    with open(credentials_path + "config", "r") as f:
        lines = f.readlines()
        for line in lines:
            if "region" in line:
                credentials["region_name"] = line.split("=")[1].strip()
    credentials["endpoint_url"] = (
        "https://s3." + credentials["region_name"] + ".io.cloud.ovh.net/"
    )
    return credentials
