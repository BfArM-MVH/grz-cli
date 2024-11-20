"""Module for uploading encrypted submissions to a remote storage"""

from __future__ import annotations

import logging
import re
from os import PathLike
from pathlib import Path

import boto3  # type: ignore[import-untyped]
import botocore.handlers  # type: ignore[import-untyped]
from boto3 import client as boto3_client  # type: ignore[import-untyped]
from botocore.config import Config as Boto3Config  # type: ignore[import-untyped]

from .models.config import ConfigModel

MULTIPART_THRESHOLD = 8 * 1024 * 1024  # 8MiB, boto3 default
MULTIPART_CHUNKSIZE = 8 * 1024 * 1024  # 8MiB, boto3 default
MULTIPART_MAX_CHUNKS = 1000  # CEPH S3 limit, AWS limit is 10000

log = logging.getLogger(__name__)

# see discussion: https://github.com/boto/boto3/discussions/4251 to accept bucket names with ":" in the name
botocore.handlers.VALID_BUCKET = re.compile(r"^[:a-zA-Z0-9.\-_]{1,255}$")  # type: ignore[import-untyped]


class S3BotoDownloadWorker:
    """Implementation of an upload worker using boto3 for S3"""

    __log = log.getChild("S3BotoDownloadWorker")

    def __init__(self, config: ConfigModel, status_file_path: str | PathLike):
        """
        An download manager for S3 storage

        :param config: The configuration model
        :param status_file_path: The path to the status file
        """
        super().__init__()

        self._status_file_path = Path(status_file_path)
        self._config = config

        self._init_s3_client()

    def _init_s3_client(self):
        # if user specifies empty strings, this might be an issue
        def empty_str_to_none(string: str | None) -> str | None:
            if string == "" or string is None:
                return None
            else:
                return string

        # configure proxies if proxy_url is defined
        proxy_url = empty_str_to_none(self._config.s3_options.proxy_url)
        if proxy_url is not None:
            config = Boto3Config(proxies={"http": proxy_url, "https": proxy_url})
        else:
            config = None

        # Initialize S3 client for uploading
        self._s3_client: boto3.session.Session.client = boto3_client(
            service_name="s3",
            region_name=empty_str_to_none(self._config.s3_options.region_name),
            api_version=empty_str_to_none(self._config.s3_options.api_version),
            use_ssl=empty_str_to_none(self._config.s3_options.use_ssl),
            endpoint_url=empty_str_to_none(str(self._config.s3_options.endpoint_url)),
            aws_access_key_id=empty_str_to_none(self._config.s3_options.access_key),
            aws_secret_access_key=empty_str_to_none(self._config.s3_options.secret),
            aws_session_token=empty_str_to_none(self._config.s3_options.session_token),
            config=config,
        )

    def prepare_download(
        self,
        metadata_dir: Path,
        files_dir: Path,
        encrypted_files_dir: Path,
        log_dir: Path,
    ):
        """
        Prepare the download of an encrypted submission

        :param metadata_dir: Path to the metadata directory
        :param files_dir: Path to the files directory
        :param encrypted_files_dir: Path to the encrypted_files directory
        :param log_dir: Path to the logs directory
        """
        for dir_path in [metadata_dir, files_dir, encrypted_files_dir, log_dir]:
            if not dir_path.exists():
                dir_path.mkdir(parents=False, exist_ok=False)  # Create the directories

    def download(
        self,
        submission_id: str,
        metadata_dir: Path,
        encrypted_files_dir: Path,
        metadata_file_name: str = "metadata.json",
    ):
        """
        Download an encrypted submission

        :param submission_id: The ID of the submission to download
        :param metadata_dir: The path to the metadata directory
        :param encrypted_files_dir: The path to the encrypted files directory
        :param metadata_file_name: The name of the metadata file
        """
        bucket_name = self._config.s3_options.bucket

        metadata_key = f"{submission_id}/metadata/{metadata_file_name}"
        encrypted_files_key_prefix = f"{submission_id}/files"

        metadata_file_path = metadata_dir / metadata_file_name

        self.download_file(metadata_key, metadata_file_path)

        response = self._s3_client.list_objects_v2(
            Bucket=bucket_name, Prefix=encrypted_files_key_prefix
        )

        if "Contents" in response:
            for file in response["Contents"]:
                if file["Size"] == 0:
                    continue
                else:
                    file_key = file["Key"]
                    file_path = Path(file_key).relative_to(f"{submission_id}/files")
                    print(file_path)
                    file_path = encrypted_files_dir / file_path
                    file_path.parent.mkdir(mode=0o770, parents=True, exist_ok=True)
                    self.download_file(file_key, file_path)

    def download_file(self, s3_object_id: str, local_file_path: PathLike | str):
        """
        Download a single file from S3

        :param s3_object_id: The S3 object ID to download
        :param local_file_path: The path to save the downloaded file
        """
        self.__log.info(f"Downloading {s3_object_id} to {local_file_path}...")
        self._s3_client.download_file(
            self._config.s3_options.bucket, s3_object_id, local_file_path
        )

        self.__log.debug("DONE !!")
