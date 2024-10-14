from __future__ import annotations

import abc
import logging
from hashlib import sha256
from os.path import getsize
from pathlib import Path
from traceback import format_exc
from typing import Dict, override

import boto3
from boto3 import client as boto3_client
from botocore.config import Config as boto3_config
from tqdm.auto import tqdm

from grz_upload.parser import EncryptedSubmission

log = logging.getLogger(__name__)


class UploadError(Exception):
    pass


class UploadWorker(metaclass=abc.ABCMeta):

    def upload(self, encrypted_submission: EncryptedSubmission, submission_id: str):
        for local_file_path, file_info in encrypted_submission.encrypted_files.items():
            relative_file_path = file_info["relative_file_path"]
            s3_object_id = Path(submission_id) / "files" / relative_file_path

            try:
                self.upload_file(local_file_path, s3_object_id)
            except Exception as e:
                raise UploadError(f"Failed to upload {local_file_path}") from e

    @abc.abstractmethod
    def upload_file(self, local_file_path: str | Path, s3_object_id: str):
        raise NotImplementedError()


class S3BotoUploadWorker(UploadWorker):
    __log = log.getChild("S3BotoUploadWorker")

    MULTIPART_CHUNK_SIZE = 200 * 1024 * 1024  # 200 MB
    MAX_SINGLEPART_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

    def __init__(self, s3_settings: Dict[str, str], status_file_path: str | Path):
        """
        An upload manager for S3 storage

        :param s3_settings: settings for boto3 containing the following fields:
            - s3_access_key (required)
            - s3_secret (required)
            - region_name
            - api_version
            - use_ssl
            - s3_url
            - s3_session_token
            - proxy_url
        :param s3_submission_prefix: Prefix of this submission on the S3 bucket
        :param status_file_path: file for storing upload state. Can be used for e.g. resumable uploads.
        """
        super().__init__()

        self._status_file_path = Path(status_file_path)
        self._s3_settings = s3_settings

        self._init_s3_client()

    def _init_s3_client(self):
        # if user specifies empty strings, this might be an issue
        def empty_str_to_none(string: str):
            if string == "":
                return None
            else:
                return string

        # configure proxies if proxy_url is defined
        proxy_url = empty_str_to_none(self._s3_settings.get("s3_session_token", None))
        if proxy_url is not None:
            config = boto3_config(
                proxies={
                    'http': proxy_url,
                    'https': proxy_url
                }
            )
        else:
            config = None

        # Initialize S3 client for uploading
        self._s3_client: boto3.session.Session.client = boto3_client(
            service_name='s3',
            region_name=empty_str_to_none(self._s3_settings.get("region_name", None)),
            api_version=empty_str_to_none(self._s3_settings.get("api_version", None)),
            use_ssl=empty_str_to_none(self._s3_settings.get("use_ssl", None)),
            endpoint_url=empty_str_to_none(self._s3_settings.get("s3_url", None)),
            aws_access_key_id=empty_str_to_none(self._s3_settings.get("s3_access_key", None)),
            aws_secret_access_key=empty_str_to_none(self._s3_settings.get("s3_secret", None)),
            aws_session_token=empty_str_to_none(self._s3_settings.get("s3_session_token", None)),
            config=config
        )

    # def show_information(self):
    #     self.__log.info(f"total files in metafile: {self.__file_total}")
    #     self.__log.info(f"uploaded files: {self.__file_done}")
    #     self.__log.info(f"failed files: {self.__file_failed}")
    #     self.__log.info(
    #         f"already finished files before current upload: {self.__file_prefinished}"
    #     )

    def _multipart_upload(self, local_file, s3_object_id):
        """
        Upload the file in chunks to S3.

        :param file_location: pathlib.Path()
        :param s3_object_id: string
        :return: sha256 value for uploaded file
        """
        multipart_upload = self._s3_client.create_multipart_upload(
            Bucket=self._s3_settings["s3_bucket"], Key=s3_object_id
        )
        upload_id = multipart_upload["UploadId"]
        parts = []
        part_number = 1

        # Get the file size for progress bar
        file_size = getsize(local_file)
        # initialize progress bar
        progress_bar = tqdm(
            total=file_size, unit="B", unit_scale=True, unit_divisor=1024
        )

        try:
            # Initialize sha256 calculations
            original_sha256 = sha256()

            with open(local_file, "rb") as infile:
                # Process the file in chunks
                while chunk := infile.read(S3BotoUploadWorker.MULTIPART_CHUNK_SIZE):
                    original_sha256.update(chunk)
                    # Upload each chunk
                    part = self._s3_client.upload_part(
                        Bucket=self._s3_settings["s3_bucket"],
                        Key=s3_object_id,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=chunk,
                    )
                    progress_bar.update(len(chunk))
                    parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
                    part_number += 1

            # Complete the multipart upload
            self._s3_client.complete_multipart_upload(
                Bucket=self._s3_settings["s3_bucket"],
                Key=s3_object_id,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
            progress_bar.close()  # close progress bar
            return original_sha256.hexdigest()

        except Exception as e:
            for i in format_exc().split("\n"):
                log.error(i)
            self._s3_client.abort_multipart_upload(
                Bucket=self._s3_settings["s3_bucket"], Key=s3_object_id, UploadId=upload_id
            )
            raise e

    def _upload(self, local_file, s3_object_id):
        """
        Upload the file to S3.

        :param file_location: pathlib.Path()
        :param s3_object_id: string
        :return: sha256 values for original file
        """
        try:
            with open(local_file, "rb") as fd:
                # calculate sha256sum
                # original_sha256 = sha256(data)

                # Upload data
                self._s3_client.put_object(
                    Bucket=self._s3_settings["s3_bucket"], Key=s3_object_id, Body=fd
                )
            # return original_sha256.hexdigest()
        except Exception as e:
            raise e

    @override
    def upload_file(self, local_file_path, s3_object_id):
        self.__log.info(f"Uploading {local_file_path} to {s3_object_id}...")

        # Get the file size to decide whether to use multipart upload
        file_size = getsize(local_file_path)
        if file_size > S3BotoUploadWorker.MAX_SINGLEPART_UPLOAD_SIZE:
            # do multipart upload
            sha256sums = self._multipart_upload(local_file_path, s3_object_id)
        else:
            sha256sums = self._upload(local_file_path, s3_object_id)
