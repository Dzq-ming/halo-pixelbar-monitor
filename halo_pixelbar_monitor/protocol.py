"""Bounded text/display commands for the tested A160 HID control interface.

No serial numbers are returned or written to disk. This is a community
implementation, not an official SDK. See docs/PROTOCOL.md and THIRD_PARTY.md.
"""
import time

VID, PID, INTERFACE, USAGE_PAGE, USAGE = 0x2D99, 0xA160, 4, 0xFF14, 1
ALIGNMENTS = {"left": 0, "center": 1, "right": 2, "stretch": 3}


class ProtocolError(RuntimeError):
    pass


def packet(command, payload=()):
    payload = bytes(payload)
    data = bytearray([0x2E, 0xAA, 0xEC, command, len(payload) >> 8, len(payload) & 255])
    data.extend(payload)
    data.append(sum(data[1:]) & 255)
    if len(data) > 64:
        raise ValueError("HID packet exceeds 64 bytes")
    return bytes(data).ljust(64, b"\0")


def parse_reply(reply, command):
    reply = bytes(reply)
    if len(reply) < 7 or reply[0] != 0x2F or reply[1] not in (0xBB, 0xCC) or reply[2:4] != bytes([0xEC, command]):
        return None
    size = int.from_bytes(reply[4:6], "big")
    if size > 57 or len(reply) < size + 7 or sum(reply[1:6+size]) & 255 != reply[6+size]:
        return None
    return reply[6:6+size]


class Screen:
    def __init__(self, device=None):
        if device is None:
            import hid
            matches = [d for d in hid.enumerate(VID, PID)
                       if d.get("interface_number") == INTERFACE
                       and d.get("usage_page") == USAGE_PAGE and d.get("usage") == USAGE
                       and "pixelbar" in str(d.get("product_string", "")).lower()]
            if len(matches) != 1:
                raise ProtocolError("Expected exactly one supported PixelBar")
            device = hid.device()
            try:
                device.open_path(matches[0]["path"])
            except Exception:
                device.close()
                raise
        self.device = device
        self.color = self.alignment = None

    def request(self, command, payload=()):
        # Bound the drain loop even if another controller is continuously active.
        for _ in range(32):
            if not self.device.read(64, 1):
                break
        frame = packet(command, payload)
        if self.device.write(frame) != 64:
            raise ProtocolError("Incomplete HID write")
        deadline = time.monotonic() + 1
        while time.monotonic() < deadline:
            parsed = parse_reply(self.device.read(64, 100), command)
            if parsed is not None:
                return parsed
        raise ProtocolError("No valid reply")

    def snapshot(self):
        state, text = self.request(0xEE), self.request(0xE7, [0])
        if len(state) < 9 or len(text) < 4 or len(text) < 4 + text[3]:
            raise ProtocolError("Incomplete screen snapshot")
        return {"state": state.hex(), "text": text.hex()}

    def show(self, text, color=(102, 200, 255), alignment="center"):
        # Only known ASCII glyphs are used by the dashboard. Character receipt
        # does not imply that an arbitrary Unicode glyph exists in firmware.
        if not text or not text.isascii() or len(text) > 32 or any(ord(c) < 32 or ord(c) > 126 for c in text):
            raise ValueError("Use 1-32 printable ASCII characters")
        if alignment not in ALIGNMENTS or len(color) != 3 or any(type(c) is not int or not 0 <= c <= 255 for c in color):
            raise ValueError("Invalid display settings")
        if self.color != color:
            self.request(0xEF, [3, *color, 0, 0, 255, 255, 255])
            self.color = color
        if self.alignment != alignment:
            self.request(0xEF, [1, *color, 0, 2, 0, ALIGNMENTS[alignment], 255])
            self.alignment = alignment
        data = text.encode("ascii")
        if self.request(0xE8, [0, len(data), *data]) != b"\x01":
            raise ProtocolError("Device rejected text")
        actual = self.request(0xE7, [0])
        if len(actual) < 4 or actual[3] != len(data) or actual[4:4+len(data)] != data:
            raise ProtocolError("Text readback mismatch")

    def restore(self, snapshot):
        state, text = bytes.fromhex(snapshot["state"]), bytes.fromhex(snapshot["text"])
        if len(state) < 9 or len(text) < 4 or len(text) < 4 + text[3]:
            raise ProtocolError("Invalid saved screen snapshot")
        self.request(0xE8, [text[0], text[3], *text[4:4+text[3]]])
        settings = [1, *state[1:9]]
        self.request(0xEF, [3, *settings[1:4], 0, 0, 255, 255, 255])
        self.request(0xEF, settings)

    def close(self):
        self.device.close()
