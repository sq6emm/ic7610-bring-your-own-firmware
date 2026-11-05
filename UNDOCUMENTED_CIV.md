# Undocumented CI-V commands (IC-7610)

Commands implemented in the IC-7610 firmware that are **not listed in Icom's public CI-V reference guide**.
Recovered by reverse-engineering the firmware (dispatch tables + handler code). (The IC-705 / IC-9700 / IC-905
have an analogous service block — documented in their own repository; the IC-705 one was confirmed on real
hardware.)

> ⚠️ **WARNING.** Some of these are **factory service** commands that **reset the radio, enter calibration/
> alignment mode, or write raw calibration data** — including the Ethernet MAC address. Sending them can **wipe
> your settings** or **misalign the radio** (hard to undo without test equipment). *Read* commands are safe;
> *writes/actions* are not. This documents **what exists** — it is not a recommendation to use it. Use only on a
> radio you own, with backups.

## Frame recap
`FE FE <to> <from> <cmd> [<sub>] [<data>] FD`. Default IC-7610 address = `0x98`; controller = `0xE0`.
Reply `…FB`=OK, `…FA`=NG (rejected).

---

## 1. Factory service block — command `0x1A`, sub `0xD0`–`0xE6`
A hidden factory interface under the standard `0x1A` (settings) command. **Every sub below was read from the
IC-7610's own dispatch table and handler code.** The IC-7610 has no D-STAR, so unlike the handheld/VHF radios it
has **no DV self-test** — instead its password-gated secondary slot is an **Ethernet MAC-address write**.

### What each sub-command does (plain language)

**🟢 Reads — safe, no password**
- **`1A D5`** — *Read the region/destination code* (which market → which bands it may transmit).
- **`1A D6`** — *Read an internal calibration measurement* (a raw sensor/ADC reading).
- **`1A E4`** — *Read a minor service value.*

**🔧 Adjustment / MAC write — password required**
Passwords (ASCII, sent as the command data):

| Function | Sub | Password |
|---|---|---|
| Enter factory alignment mode | `1A E0` | `SX-3864 Adjust` |
| **Write the Ethernet MAC address** | `1A D7` | `SX-3864 MAC Write` |

- **`1A E0` + "`SX-3864 Adjust`"** — *Enter the factory alignment/adjustment mode* (the on-screen service menu a
  technician uses to calibrate the radio). Internally it flips the radio into "service state 1".
- **`1A D7` + "`SX-3864 MAC Write`"** — *Write the radio's Ethernet (LAN) MAC address.* This slot is unique to
  the IC-7610 among this family because it is the model with a wired network port. It takes the address bytes
  after the password and programs them. Changing a device's MAC is normally a factory-only operation.

**🔴 Reset / writes / actions — NO password**
- **`1A D0`** — **FACTORY RESET. Clears all settings to defaults. No password.** Internally enters "service
  state 3" and zeroes the working data structures.
- **`1A E1`** — *A second reset/clear variant* ("service state 2"); only guard is that one data byte must be 0.
- **`1A D1`** — *Set a service/test-mode flag* (0/1); needs an internal permission bit already set.
- **`1A D3`** — *Run a service diagnostic* and return the result as a CI-V frame (only in a safe state).
- **`1A E2` / `E3` / `E5`** — *Service writes*: select a service sub-mode / pick the target of the next service
  operation / write a service data value addressed by a byte in the command.
- **`1A E6`** — reserved (no handler).

---

## 2. Other undocumented command — `0x2A`
Not in the public reference; three sub-commands:
- **`2A 00`** — reads/writes **13-byte VFO/frequency records** (a ring of four — memo-pad / quick-recall style).
- **`2A 01`** — extended **antenna / tuner** control.
- **`2A 02`** — has a further sub-level (additional parameters).

---

## How these were found
Decompile the firmware main image → locate the CI-V command dispatcher (a table of command → handler pointers)
→ read each handler, confirming which `0x1A` service subs exist and what each does. The passwords were recovered
from the firmware's text (rodata). The analogous IC-705 service block was additionally verified live over USB
CI-V (its `SX-4075 Adjust` password unlocked the on-screen service menu), which cross-confirms this family of
commands.

## Responsible use
This describes what the firmware implements. The service / reset / adjust / MAC-write commands are dangerous
(data loss, misalignment, a changed network identity). Don't rely on undocumented commands for anything
important — Icom may change them without notice. No firmware is included or required to read this document.
