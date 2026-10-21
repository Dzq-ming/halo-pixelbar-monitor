# Tested text protocol and evidence boundaries

The verified speaker is **Halo PixelBar 2026 upgraded edition**, USB VID `2D99`,
PID `A160`, interface `4`, usage page `FF14`, usage `1`. These public product
identifiers are not a device serial. Other PIDs remain outside the allowlist.

This is a community implementation based on the references in `THIRD_PARTY.md`
and local hardware validation. No official protocol specification is claimed.

## Frames

Requests are padded to exactly 64 bytes:

```text
2E AA EC command length_hi length_lo payload checksum padding
```

The checksum is the byte sum beginning at `AA`, modulo 256. A normal query
response starts `2F BB EC`; a set acknowledgement may start `2F CC EC`.
Lengths and checksums are validated before consuming payloads. A write result
alone is never treated as successful text rendering.

| Command | Use in this project |
| --- | --- |
| `EE` | Query previous screen state |
| `E7`, payload `00` | Query previous/current custom text |
| `E8` | Set text: source `00`, UTF-8 byte length, text bytes |
| `EF` | Set bounded screen color and static alignment fields |

On this revision an `E7` response contains source, maximum character count,
maximum package size, text byte length, then text bytes. Text comparison starts
after these four metadata bytes. A text-write success acknowledgement is `01`.

The dashboard uses 32 printable ASCII characters. Actual 32-character static
display has been visually confirmed on the tested device. An arbitrary non-ASCII
glyph can be received and read back while still being absent from the firmware
font; `°` and `℃` did not render in the observed setup.

## State restoration

Before the first change, the application queries screen state and text and saves
them under ignored `runtime/`. It restores the original custom text, theme RGB,
and the first nine screen-setting bytes when stopping. The snapshot is not
overwritten on a reconnect. Device power loss or a forced process termination
may prevent restoration. This is not a backup of the entire device configuration.

## Pixel drawing

The existing 64-byte EC-family text path works. The separate ED/01 canvas/screen
query used by a newer software path did not answer in repeated bounded probes
on the tested A160 setup. A legacy custom-image file-transfer path also exists,
but its file format and suitability for continuous updates have not been
established here.

Those observations do not prove that the hardware can never display custom
pixels. They mean this release does not have a verified live framebuffer,
multi-line renderer, font-size control or 2-row dashboard. No firmware update,
factory reset, arbitrary raw-packet API, or image-upload experiment is included.
