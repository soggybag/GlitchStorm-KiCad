# GlitchStorm v2 — KiCad migration, review and fix plan

2026-09-29. Source: `~/Documents/eagle/projects/GlitchStorm-v2/GlitchStorm-v2.sch/.brd` (Sept 2025; sch == brd, checked).
Faithful transcription: `GlitchStorm KiCad/GlitchStorm.kicad_sch` (+pdf). Generator and `check_vs_eagle.py` are in `scripts/`. ERC 0, netlist == Eagle board.

## What's there

- **Arduino Nano** module (bytebeat firmware).
  - **POT1–3 + RATE** (9 mm) on **A0–A3** (pin 3 to 5 V, pin 1 to GND).
  - **Buttons** S3/S4 on **D3/D4** to GND (firmware pull-ups).
  - **4 LEDs** on **D7–D10**, each through R1–R4 to GND.
- **Audio:** **D11 PWM** → C6 100n to GND *directly on the pin* → C5 100n → **VOL** pot → **LM386** (pins 1–8: 10µ = **gain 200**; pin 7 47µ bypass) → C2 47µ → **stereo jack, tip + ring tied**.
- **Power:** only the Nano's 5 V (USB). C1 47µ. VIN is not wired, and there's no DC jack.
- **Board:** 77 × 77 mm, THT everywhere. **All tracks 0.15 mm (6 mil), including power and audio.** Mostly bottom-layer routing, one via, a top GND pour.

## Problems found

### Electrical
1. **D11 drives C6 (100n) with no series resistor.** It isn't a filter, just a capacitive short on each PWM edge (peak currents far above the ATmega's pin rating). Stressful for the MCU and noisy on the 5 V/ground.
2. **No real PWM filter.** The PWM carrier (tens of kHz) goes straight into the LM386.
3. **LM386 gain 200** on a signal that is already ~5 Vpp before VOL. Most of the VOL travel is clipping; noise and hiss are amplified 200×.
4. **No Zobel** (10 Ω + 47n) on the LM386 output. The LM386 is prone to oscillating into cables or headphones without it.
5. **LM386 on the Nano's 5 V:** digital and USB noise goes straight into the amp, and a 5 V rail gives little output swing.
6. **Stereo jack with tip + ring tied:** a *mono* plug shorts the ring to the sleeve, i.e. the LM386 output (through C2) straight to ground.
7. **C5 100n into VOL:** if VOL is 10k, that's a 160 Hz high-pass (thin bass). Pot values aren't recorded anywhere.
8. **Missing values:** R1–R4 (LED resistors) and all five pots have no value in the Eagle file.
9. **No decoupling** at the LM386 supply pin, and only one ground connection to the Nano.
10. **No external power:** USB only (and no reverse protection, if a DC input is added).

### Layout
11. **6 mil tracks everywhere**, including 5 V, ground returns and the speaker/headphone output. Too thin for the LM386's output current, and fragile.
12. **Ground:** no star or analog return. The LM386 output current shares the ground path with the Nano's digital return and the pot references (ADC noise, zipper and whine).
13. The board is large (77 × 77) for its content, with no enclosure reference. Parts are scattered.

## Proposed fixed design (GlitchStorm v3)

- **Keep the Nano module on headers** (easy firmware updates, socketable), and **keep the same pin map** so the existing firmware runs unchanged (A0–A3, D3/D4, D7–D10, D11 audio).
- **Audio chain:**
  1. D11 → **1k** → 10n → **1k** → 10n: a 2nd-order RC low-pass at ~16 kHz, which suppresses the PWM carrier.
  2. → **1µ DC block** → **VOL (A10k)**.
  3. → output stage: either an **op-amp line out** (TL072/MCP6002, low noise) *or* an **LM386 at gain 20** (C4 removed or with a resistor) with a **Zobel**, **100n + 100µ decoupling**, and **its own supply**.
- **Output jack:** decide mono TS (line/amp) vs stereo TRS (headphones). If TRS, feed tip and ring through **~47–100 Ω each** so a mono plug can't short the amp.
- **Power:**
  - **9 V pedal jack** → SS14 → **Nano VIN** (the Nano's regulator makes 5 V for the MCU). The audio stage runs from the filtered 9 V (more headroom, less digital noise).
  - Keep USB for programming. The Nano handles USB/VIN selection, but check that the v3 board doesn't back-feed.
- **Controls:**
  - Pots **B10k** on the ADC inputs (ADC wants ≤10k source), with an optional **100n** on each ADC pin.
  - **LED resistors 1k–2k2**.
  - Optional **100n debounce** on the buttons.
- **SMD vs THT:** passives SMD 0805 (JLC); pots, jack, buttons, LEDs and Nano headers THT, hand-soldered, like the other projects.
- **Layout:** 0.25 mm signal / **0.5 mm power and audio output**, GND pour on both layers, star ground at the output stage, and separate the Nano's digital return from the audio ground.
- **Form factor:** decide the target (standalone desktop box, pedal enclosure, Eurorack?) before layout.

## Open questions (for the user)

1. **Use case:** headphones or a small speaker (keep the LM386), or line out into amps/pedals/mixer (op-amp line out)? Or both?
2. **Power:** USB only, or add a 9 V pedal-style DC jack (VIN)?
3. **Form factor / enclosure:** same 77 × 77 board, a pedal enclosure, Eurorack, or something else?
4. **What went wrong with v2** in use: noise or whine, distortion, oscillation, mechanical fit, assembly pain?
5. **Values actually used:** pots (10k?), LED resistors, VOL pot.
6. Firmware: keep the current pin map (assumed yes).

## To-do

- [ ] User answers the questions above.
- [ ] Draw the GlitchStorm v3 schematic (fixed), with the same pin map.
- [ ] Choose the enclosure/board size → layout → JLC.
- [ ] Bench-check the PWM filter and output level; confirm the firmware's PWM frequency.
