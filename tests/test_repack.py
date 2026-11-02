import os
import random
import unittest

from icom_rza1_decode import lzss_decompress, autokey_decode
from ic_rza1_repack import lzss_compress, autokey_encode


class RepackPrimitiveTests(unittest.TestCase):
    def test_lzss_roundtrip(self):
        rnd = random.Random(1)
        cases = [b"", b"X", b"ABCABCABC", b"A" * 64, bytes(range(20)) * 5,
                 bytes(rnd.getrandbits(8) for _ in range(6000)),
                 bytes(rnd.randrange(4) for _ in range(8000))]
        for s in cases:
            dec = lzss_decompress(lzss_compress(s), len(s))[0] if s else b""
            self.assertEqual(dec, s)

    def test_autokey_exact_inverse(self):
        rnd = random.Random(2)
        data = bytes(rnd.getrandbits(8) for _ in range(9000))
        for base, key, iv in [(0x34, 0xf4, 0x89), (0x64, 0x19, 0x9b)]:
            enc = autokey_encode(data, base, key, iv)
            self.assertEqual(autokey_decode(enc, base, key, iv)[0], data)


@unittest.skipUnless(os.path.exists("7610_145.dat"), "needs a user-supplied IC-7610 .dat")
class RepackContainerTest(unittest.TestCase):
    def test_identity_repack_valid(self):
        from ic_rza1_repack import _selftest
        _selftest("7610_145.dat")


if __name__ == "__main__":
    unittest.main()
