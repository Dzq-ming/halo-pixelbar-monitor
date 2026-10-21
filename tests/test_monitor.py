import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime

from halo_pixelbar_monitor.config import DEFAULTS, read_config
from halo_pixelbar_monitor.formatting import dashboard
from halo_pixelbar_monitor.protocol import Screen, packet, parse_reply, ProtocolError


def reply(command, payload, acknowledgement=False):
    frame = bytearray([0x2F, 0xCC if acknowledgement else 0xBB, 0xEC, command, 0, len(payload), *payload])
    frame.append(sum(frame[1:]) & 255)
    return bytes(frame).ljust(64, b'\0')


class FakeDevice:
    def __init__(self, mismatch=False):
        self.queue = []
        self.writes = []
        self.text = b'INITIAL'
        self.state = bytes([0, 100, 150, 200, 0, 1, 6, 0, 255, 1, 0, 0])
        self.mismatch = mismatch
    def read(self, size, timeout):
        return self.queue.pop(0) if self.queue else []
    def write(self, data):
        self.writes.append(data)
        command = data[3]
        payload = data[6:6+int.from_bytes(data[4:6], 'big')]
        if command == 0xE8:
            self.text = payload[2:2+payload[1]]
            self.queue.append(reply(command, [1], True))
        elif command == 0xE7:
            text = b'WRONG' if self.mismatch else self.text
            self.queue.append(reply(command, [0, 16, 50, len(text), *text]))
        elif command == 0xEE:
            self.queue.append(reply(command, self.state))
        else:
            self.queue.append(reply(command, [1], True))
        return len(data)
    def close(self):
        pass


class LayoutTests(unittest.TestCase):
    def test_fixed_positions_through_digit_boundaries(self):
        for value in (0, 9, 10, 99, 100):
            data = dict(cpu_temp=value, cpu_load=value, gpu_temp=value, gpu_load=value, memory_load=value)
            text = dashboard(data, datetime(2030,1,1,23,59))
            self.assertEqual(len(text), 32)
            self.assertTrue(text.isascii())
            self.assertEqual([text.index('|'), text.index('|',10), text.index('|',20)], [9,19,25])
            self.assertEqual(text[27:], '23:59')
        self.assertIn('C100/100', text)
    def test_bad_or_absent_values_keep_placeholders(self):
        data = dict(cpu_temp=float('nan'), cpu_load=101, gpu_temp=-1, gpu_load=float('inf'))
        self.assertEqual(dashboard(data, datetime(2030,1,1,0,0)), ' C--/--  | G--/--  | M-- | 00:00')


class ProtocolTests(unittest.TestCase):
    def test_reject_corrupt_or_wrong_response(self):
        good = reply(0xE7, [0,16,50,1,65])
        self.assertIsNotNone(parse_reply(good, 0xE7))
        self.assertIsNone(parse_reply(good, 0xEE))
        bad = bytearray(good)
        bad[6] ^= 1
        self.assertIsNone(parse_reply(bad, 0xE7))
        self.assertIsNone(parse_reply(good[:8], 0xE7))
    def test_snapshot_write_and_restore(self):
        device = FakeDevice()
        screen = Screen(device)
        saved = screen.snapshot()
        screen.show('A'*32)
        self.assertEqual(device.text, b'A'*32)
        screen.restore(saved)
        self.assertEqual(device.text, b'INITIAL')
        self.assertTrue(all(len(w)==64 for w in device.writes))
    def test_readback_mismatch_is_not_success(self):
        with self.assertRaises(ProtocolError):
            Screen(FakeDevice(True)).show('VALID')
    def test_invalid_text_never_writes_to_device(self):
        device = FakeDevice()
        for text in ('A'*33, '\u00b0C', 'A\nB', ''):
            with self.assertRaises(ValueError):
                Screen(device).show(text)
        self.assertEqual(device.writes, [])
    def test_oversized_packet_rejected(self):
        with self.assertRaises(ValueError):
            packet(0xE8, b'A'*58)


class ConfigTests(unittest.TestCase):
    def test_defaults_and_valid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'config.json'
            self.assertEqual(read_config(path), DEFAULTS)
            path.write_text(json.dumps({'alignment':'left'}), encoding='utf8')
            self.assertEqual(read_config(path)['alignment'], 'left')
    def test_reject_invalid_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'config.json'
            for value in ({'alignment':'bad'}, {'refresh_seconds':0}, {'gpu_index':-1}, {'gpu_index':True}, {'restore_on_exit':'yes'}, {'secret':'not accepted'}):
                path.write_text(json.dumps(value),encoding='utf8')
                with self.assertRaises(ValueError):
                    read_config(path)


if __name__ == '__main__':
    unittest.main()
