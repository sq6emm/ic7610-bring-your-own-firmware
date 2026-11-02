# Icom IC-7610 firmware tools

Tooling and documentation to decode the Icom **IC-7610** firmware update container
(`.dat`) — the main-CPU image and its byte codec.

> **No firmware is included.** Bring your own `.dat` from Icom's official firmware
> update. This repository contains only tooling and format documentation.

## Result

The IC-7610 uses the same two-stage, fully reversible protection as the rest of Icom's
RZ/A1 radios (IC-705 / IC-9700 / IC-905):

1. **Autokey byte transform** — `plain[i] = stored[i] XOR ((prev_plain + pos - KEY) & 255)`,
   feedback on the previous *plaintext* byte, anchored by the `0xFF` erased-flash padding.
2. **Okumura LZSS** — 4096-byte ring, cursor `0xFEE`, LSB-first flags, `len = (hi & 15) + 3`,
   `index = lo | ((hi & 0xF0) << 4)`, terminated by an explicit output length.

Recovered, model-specific parameters (auto-derived, no configuration needed):

| Parameter | IC-7610 |
|---|---|
| `KEY` (from the `0xFF` ramp) | `0xf4` |
| main-domain start | `0x34` |
| main LZSS stream offset | `+0x10004` (4-byte length header) |
| main image | ARMv7-A, load `0x20005000`, entry `0x20005050` |

The decoded main image starts with the ARM reset-vector table (`18 F0 9F E5 …`) and
contains `IC-7610`, `ICOM` and `Icom` strings — real decompressed firmware, not an
entropy- or heuristic-selected candidate.

## Usage

```sh
# Decode an IC-7610 firmware file you supply yourself:
python3 icom_rza1_decode.py 7610_145.dat out/7610
```

Writes `bootstrap.bin`, `main.bin`, `main.elf` (load address set for analysis) and
`manifest.json`. `icom_rza1_decode.py` auto-derives the KEY, the domain start, the main
stream offset and the output length, so the same tool also decodes IC-705, IC-9700 and
IC-905.

## Re-packing

`ic_rza1_repack.py` closes the loop — a decompressed main-CPU image is re-compressed and
re-sealed into a container the format accepts:

```python
from ic_rza1_repack import repack
raw = open("7610_145.dat", "rb").read()
image = open("out/7610/main.bin", "rb").read()      # patch this image as you like
open("7610_145.patched.dat", "wb").write(repack(raw, image))
```

The LZSS encoder (lazy matching) round-trips bit-for-bit through the decoder and runs ~2%
under Icom's own size; the autokey transform is an exact inverse. An **identity re-pack**
(same image) produces a valid-MD5 container (IC-7610 MD5 region `0x400000`) that re-decodes
to the identical image — only the main slot and the 16-byte digest change.

## Scope and limits

- Verified on IC-7610 firmware (v1.44 / v1.45): main-CPU image recovered, ARM vectors
  and `IC-7610`/`ICOM` strings confirmed.
- The IC-7610 container is multi-component (DSP / data / other images in addition to the
  main CPU); this tool recovers the **main-CPU image**. Per-component extraction of the
  remaining images is a follow-up.
- Whether a real radio accepts a rebuilt image is **unverified**.

## Acknowledgements

Emulation of this radio builds on the reverse-engineering of the closely related Icom
**IC-7300**, which uses the same Renesas RZ/A1 SoC family:

- [jeskko/ic7300-homebrew](https://github.com/jeskko/ic7300-homebrew) (MIT) — a custom
  **QEMU machine for the RZ/A1**, a homebrew SDK, and container/LZSS tooling. We use its
  QEMU/SoC work as the reference base for emulating IC-7610 firmware.
- [zarthur/ic-7300_firmware](https://github.com/zarthur/ic-7300_firmware) (MIT) — IC-7300
  firmware reverse-engineering research.

These are prior art for the **shared silicon** only; this project targets the IC-7610 and
does not redistribute their work.

## Legal

For interoperability and research. **Do not** commit or redistribute Icom firmware,
manuals or schematics. Firmware images decoded with these tools are Icom's copyrighted
work; keep them local.
