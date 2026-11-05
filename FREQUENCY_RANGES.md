# Frequency ranges & band plans — IC-7610

Per-region frequency coverage and TX band plans, reverse-engineered from the firmware. The
**destination/region** (set at the factory, cached in config) selects one of several **band plans**; each plan
defines the segments on which the radio will transmit. The IC-7610 also has **separate wideband-TX variants**
selected by the region word.

> Band plans are factory data (also in Icom's service manual). This documents **what the firmware supports**.
> Which bands you may transmit on is set by your radio's destination **and by your licence and local
> regulations** — always your responsibility.

HF middle bands are identical across plans and omitted for clarity:
`60m 5.255–5.405 · 30m 10.100–10.150 · 20m 14.000–14.350 · 17m 18.068–18.168 · 15m 21.000–21.450 · 12m 24.890–24.990 · 10m 28.000–29.700` (MHz).

## Coverage
- **RX:** 0.030 – 60.000 MHz, continuous — **plan-independent** (same for every region).
- **TX:** 160 m through 6 m amateur bands, plus **2200 m / 630 m** on some regions, **4 m absent** (the 7610 is
  HF + 6 m; the TX chain tops out at 54 MHz).

## The 5 band plans (region → plan)

| Plan | 2200 m | 630 m | 160 m | 80 m | 40 m | 6 m | Character |
|---|---|---|---|---|---|---|---|
| **0** | 0.1357–0.1378 | 0.472–0.479 | 1.800–2.000 | 3.500–4.000 | 7.000–7.300 | 50.0–54.0 | **USA / Americas** (full LF+HF+6m) |
| **1** | — | — | 1.800–2.000 | 3.500–4.000 | 7.000–7.300 | 50.0–54.0 | R2, no LF (60 m always on) |
| **2** | 0.1357–0.1378 | — | 1.810–2.000 | 3.500–3.800 | 7.000–7.200 | 50.0–**52.0** | **Europe (IARU R1)** |
| **3** | — | — | 1.800–2.000 | 3.500–4.000 | 7.000–7.300 | 50.0–54.0 | export (= plan 1 edges) |
| **4** | 0.1357–0.1378 | 0.472–0.479 | 1.800–1.875 **+** 1.9075–1.9125 | fragmented ×6* | 7.000–7.200 | 50.0–54.0 | **Japan (JARL)** |

`*` Plan 4 (Japan) 80 m sub-bands: `3.500–3.580 · 3.599–3.612 · 3.662–3.687 · 3.702–3.716 · 3.745–3.770 · 3.791–3.805`.
2200 m / 630 m on plans 0 and 4 are additionally gated by region sub-bits.

## ★ Wideband-TX (general-coverage) variants
Separately from the ham plan, the firmware reads two region bits to pick a **TX-range variant that overrides the
ham band plan** entirely:

| Variant | TX range |
|---|---|
| 0 | the ham band plan above |
| 1 | 1.6 – 30 MHz + 50 – 54 MHz |
| 2 | **1.6 – 54 MHz continuous** |
| 3 | **0.1 – 30 MHz + 30 – 60 MHz** (full general-coverage TX) |

**Possibilities:** on the IC-7610, broad TX expansion (the "MARS/CAP"-style continuous TX) is a **region-word
setting**, not a per-band hardware change — the firmware already contains the wideband variants. 2200 m / 630 m
are likewise region-gated. The destination is a firmware/config value, so which of these applies does not
require changing the hardware.

## How it works (mechanism)
Region word (from the on-board diode matrix, cached in config) → a lookup extracts a few bits → a plan-map byte
table → plan index → a per-plan `{low, high}` edge table that gates ham-band TX; two more region bits select the
wideband-TX variant above. RX coverage (30 kHz–60 MHz) is separate and plan-independent. The IC-705 / IC-9700
band plans (incl. the IC-705's 4 m) are documented in their own repository.

## Responsible use
Transmitting outside your licensed allocation is illegal in most jurisdictions. This is reverse-engineering
documentation of firmware behaviour; it is not advice to transmit anywhere. No firmware is included.
