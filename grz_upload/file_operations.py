import logging
from hashlib import md5
from os import urandom
from os.path import getsize

# import crypt4gh
import crypt4gh.header
import crypt4gh.keys
from nacl.bindings import crypto_aead_chacha20poly1305_ietf_encrypt
from nacl.public import PrivateKey
from tqdm.auto import tqdm

log = logging.getLogger(__name__)


def calculate_md5(file_path, chunk_size=2 ** 16):
    '''
        Calculate the md5 value of a file in chunks
        @param file_path: pathlib.Path()
        @param chunk_size: int:
        @rtype: string
        @return: calculated md5 value of file_path
        '''
    total_size = getsize(file_path)
    md5_hash = md5()
    with open(file_path, 'rb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Calculating MD5") as pbar:
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
        header_content = crypt4gh.header.make_packet_data_enc(encryption_method, session_key)
        header_packets = crypt4gh.header.encrypt(header_content, keys)
        header_bytes = crypt4gh.header.serialize(header_packets)
        return (header_bytes, session_key, keys)

    @staticmethod
    def encrypt_segment(data: bytes, key: bytes) -> bytes:
        """Encrypt 64kb block with crypt4gh"""
        nonce = urandom(12)
        encrypted_data = crypto_aead_chacha20poly1305_ietf_encrypt(data, None, nonce, key)
        return nonce + encrypted_data

    @staticmethod
    def encrypt_part(byte_string: bytes, session_key: bytes) -> bytes:
        """Encrypt incoming chunk, using session_key"""
        data_size = len(byte_string)
        enc_data = b''
        position = 0
        while True:
            data_block = b''
            # Determine how much data to read
            segment_len = min(Crypt4GH.SEGMENT_SIZE, data_size - position)
            if segment_len == 0:  # No more data to read
                break
            # Read the segment from the byte string
            data_block = byte_string[position:position + segment_len]
            # Update the position
            position += segment_len
            # Process the data in `segment`
            enc_data += Crypt4GH.encrypt_segment(data_block, session_key)
        return enc_data

    @staticmethod
    def encrypt_file(input_path, output_path, public_keys):
        raise NotImplementedError()

    @staticmethod
    def decrypt_file(input_path, output_path, private_key):
        raise NotImplementedError()
