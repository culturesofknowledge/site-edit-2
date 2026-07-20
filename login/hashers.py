import hashlib

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
from django.utils.translation import gettext_noop as _


class UnsaltedMD5PasswordHasher(BasePasswordHasher):
    """
    Incredibly insecure algorithm that you should *never* use; stores raw
    MD5 hashes with an empty salt.

    Removed from Django itself in 5.1 (deprecated in 4.1), kept here only to
    verify cofk_users.pw values carried over as-is by data_migration.py from
    the legacy emlo-edit-php system, which stored md5(password) unsalted.
    Never used to create new passwords -- see PASSWORD_HASHERS ordering in
    siteedit2/settings/base.py.
    """

    algorithm = 'unsalted_md5'

    def salt(self):
        return ''

    def encode(self, password, salt=None):
        if salt != '':
            raise ValueError('salt must be empty.')
        return hashlib.md5(password.encode()).hexdigest()

    def decode(self, encoded):
        return {
            'algorithm': self.algorithm,
            'hash': encoded,
            'salt': None,
        }

    def verify(self, password, encoded):
        encoded_2 = self.encode(password, '')
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            _('algorithm'): decoded['algorithm'],
            _('hash'): mask_hash(decoded['hash'], show=3),
        }

    def harden_runtime(self, password, encoded):
        pass
