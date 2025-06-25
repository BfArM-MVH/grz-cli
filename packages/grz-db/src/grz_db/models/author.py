import logging
import os

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

log = logging.getLogger(__name__)


class Author:
    def __init__(self, name: str, private_key_bytes: bytes):
        self.name = name
        self.private_key_bytes = private_key_bytes

    def private_key(self) -> Ed25519PrivateKey:
        from functools import partial
        from getpass import getpass

        from cryptography.hazmat.primitives.serialization import load_ssh_private_key

        passphrase = os.getenv("GRZ_DB_AUTHOR_PASSPHRASE")
        passphrase_callback = (lambda: passphrase) if passphrase else None

        if not passphrase:
            passphrase_callback = partial(getpass, prompt=f"Passphrase for GRZ DB author ({self.name}'s) private key: ")
        log.info(f"Loading private key of {self.name}…")
        private_key = load_ssh_private_key(
            self.private_key_bytes,
            password=passphrase_callback().encode("utf-8"),
        )
        if not isinstance(private_key, Ed25519PrivateKey):
            raise TypeError(f"private_key must be an Ed25519PrivateKey. Got {type(private_key)}")
        return private_key
