import unittest

KEY = 'a' * 64


class WireTests(unittest.TestCase):
    def test_signed_roundtrip_and_tamper(self):
        from flcommons_wire.protocol import encode, decode, ProtocolError
        frame = encode({'text': 'ação'}, KEY)
        self.assertEqual(decode(frame, KEY), {'text': 'ação'})
        self.assertTrue(all(b < 128 for b in frame[1:-1]))
        with self.assertRaises(ProtocolError):
            decode(frame, 'b' * 64)
        broken = bytearray(frame)
        broken[20] ^= 1
        with self.assertRaises(ProtocolError):
            decode(bytes(broken), KEY)

    def test_rejects_bad_frames_and_oversize(self):
        from flcommons_wire.protocol import encode, decode, ProtocolError
        for frame in (b'', b'\xf0\x7d\xf7', b'\xf0\x7dFC\x01\x80\xf7'):
            with self.assertRaises(ProtocolError):
                decode(frame, KEY)
        with self.assertRaises(ProtocolError):
            encode({'text': 'x' * 5000}, KEY)

    def test_nonfinite_json_is_rejected(self):
        from flcommons_wire.protocol import encode, ProtocolError
        with self.assertRaises(ProtocolError):
            encode({'value': float('nan')}, KEY)


if __name__ == '__main__':
    unittest.main()
