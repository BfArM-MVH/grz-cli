"""
Module: file_operations
This module provides functions for file operations, including calculating the MD5 value of a file,
encrypting files using Crypt4GH, and decrypting files.
Class:
    - Crypt4GH: A class that provides encryption and decryption functionalities using Crypt4GH.
Attributes:
    - Crypt4GH.Key: A type hint for the key used by Crypt4GH.
    - Crypt4GH.VERSION: The version of Crypt4GH.
    - Crypt4GH.SEGMENT_SIZE: The size of each segment for encryption.
    - Crypt4GH.FILE_EXTENSION: The file extension used for encrypted files.
"""

from hashlib import md5, sha256
from os import urandom
from os.path import getsize
import logging

# import crypt4gh
import crypt4gh.header
import crypt4gh.keys
from nacl.bindings import crypto_aead_chacha20poly1305_ietf_encrypt
from nacl.public import PrivateKey
from tqdm.auto import tqdm

log = logging.getLogger(__name__)


def calculate_sha256(file_path, chunk_size=2 ** 16):
    '''
    Calculate the sha256 value of a file in chunks

    :param file_path: pathlib.Path()
    :param chunk_size: int:
    :rtype: string
    :return: calculated sha256 value of file_path
    '''
    total_size = getsize(file_path)
    sha256_hash = sha256()
    with open(file_path, 'rb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Calculating SHA256") as pbar:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)
                pbar.update(len(chunk))
    return sha256_hash.hexdigest()


def calculate_md5(file_path, chunk_size=2 ** 16):
    """
    Calculate the md5 value of a file in chunks

    :param file_path: pathlib.Path()
    :param chunk_size: int:
    :rtype: string
    :return: calculated md5 value of file_path
    """
    total_size = getsize(file_path)
    md5_hash = md5()
    with open(file_path, "rb") as f:
        with tqdm(
                total=total_size, unit="B", unit_scale=True, desc="Calculating MD5"
        ) as pbar:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)
                pbar.update(len(chunk))
    return md5_hash.hexdigest()


class Crypt4GH(object):
    Key = tuple[int, bytes, bytes]

    VERSION = 1
    SEGMENT_SIZE = 65536
    FILE_EXTENSION = ".c4gh"

    def __init__(self, logger):
        self.__logger = logger

    @staticmethod
    def prepare_c4gh_keys(public_key_file_path: str) -> tuple[Key]:
        """
        Prepare the key format c4gh needs, while it can contain
        multiple keys for multiple recipients, in our use case there is
        a single recipient
        """
        sk = PrivateKey.generate()
        seckey = bytes(sk)
        keys = ((0, seckey, crypt4gh.keys.get_public_key(public_key_file_path)),)
        return keys

    @staticmethod
    def prepare_header(keys: tuple[Key]) -> tuple[bytes, bytes, tuple[Key]]:
        """Prepare header separately to be able to use multiupload"""
        encryption_method = 0  # only choice for this version
        session_key = urandom(32)  # we use one session key for all blocks
        # Output the header
        header_content = crypt4gh.header.make_packet_data_enc(
            encryption_method, session_key
        )
        header_packets = crypt4gh.header.encrypt(header_content, keys)
        header_bytes = crypt4gh.header.serialize(header_packets)
        return (header_bytes, session_key, keys)

    @staticmethod
    def encrypt_segment(data: bytes, process, key: bytes): # -> bytes:
        """Encrypt 64kb block with crypt4gh"""
        nonce = urandom(12)
        encrypted_data = crypto_aead_chacha20poly1305_ietf_encrypt(
            data, None, nonce, key
        )
        process(nonce)
        process(encrypted_data)
        # return nonce + encrypted_data

    @staticmethod
    def encrypt_part(byte_string: bytes, session_key: bytes, process):# -> bytes:
        """Encrypt incoming chunk, using session_key"""
        data_size = len(byte_string)
        enc_data = b""
        position = 0
        with tqdm(total=data_size, unit="B", unit_scale=True, desc="Encrypting") as pbar:
            while True:
                data_block = b""
                # Determine how much data to read
                segment_len = min(Crypt4GH.SEGMENT_SIZE, data_size - position)
                if segment_len == 0:  # No more data to read
                    break
                # Read the segment from the byte string
                data_block = byte_string[position: position + segment_len]
                # Update the position
                position += segment_len
                # Process the data in `segment`
                # enc_data += Crypt4GH.encrypt_segment(data_block, session_key)
                Crypt4GH.encrypt_segment(data_block, process, session_key)
                pbar.update(segment_len)
        # return enc_data

    @staticmethod
    def encrypt_file(input_path, output_path, public_keys):
        """
        Encrypt the file, properly handling the Crypt4GH header.

        :param file_location: pathlib.Path()
        :param s3_object_id: string
        :param keys: tuple[Key]
        :return: tuple with md5 values for original file, encrypted file
        """        
        try:
            infile = open(input_path, 'rb')
            outfile = open(output_path, 'wb')
            # prepare header
            header_info = Crypt4GH.prepare_header(public_keys)
            outfile.write(header_info[0])


            segment = bytearray(Crypt4GH.SEGMENT_SIZE)

            while True:
                segment_len = infile.readinto(segment)
                if segment_len == 0: # finito
                    break
                if segment_len < Crypt4GH.SEGMENT_SIZE: # not a full segment
                    data = bytes(segment[:segment_len]) # to discard the bytes from the previous segments
                    Crypt4GH.encrypt_segment(data, outfile.write, header_info[1])
                    break
                data = bytes(segment) # this is a full segment
                Crypt4GH.encrypt_segment(data, outfile.write, header_info[1])
            outfile.close()
            infile.close()

        except Exception as e:
            infile.close()
            outfile.close()
            raise e

    @staticmethod
    def decrypt_file(input_path, output_path, private_key):
        raise NotImplementedError()
