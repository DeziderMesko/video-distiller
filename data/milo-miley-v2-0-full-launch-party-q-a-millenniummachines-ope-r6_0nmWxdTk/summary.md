# Summary: Milo/Miley V2.0 Full Launch Party Q&A #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=r6_0nmWxdTk

---

## TL;DR
This is a Discord/livestream Q&A from Millennium Machine Works announcing the full public release of the Milo/Miley V2.0 CNC files (following the earlier "Principles" paid-beta phase). It's a loose, informal roundtable with team members and community devs covering documentation status, LDO's upcoming pre-built kit, a fourth-axis (rotary) add-on in beta, and a batch of in-progress software/firmware work (MOS "Next" plugin architecture, ATC tool libraries, input shaping). Little of it is a tutorial — it's mostly status updates and casual technical banter.

## Key points
- V2.0 files are now fully released to the public for free (self-source build); documentation is PDF-based and just went live on the website (credited to "Be Right" for the manual).
- LDO is preparing a pre-built Milo V2 kit — blocked only by sourcing specific washers; it includes CNC'd anti-backlash nuts (vs. printed) and a metal HOI-mount replacement (with a compatible shroud option), requiring 4 extra holes in the tram plate for the LDO bracket.
- MOS (the firmware/config layer built by original dev Nine Mile Shoulders) is being restructured into a plugin-based system called "Next" — moving away from monolithic config toward per-feature plugins (fourth axis, ATC, UI) that install/update independently.
- A fourth-axis (rotary) kit is in beta, built around a Zindian DN85 rotary table with two mounting options (direct bolt or 52mm zero-point plate); DJ Roomba built probing macros (steps/mm calibration, A0 leveling) with a plugin release to Printables planned shortly.
- ATC (automatic tool changer) work centers on a persistent tool library (importable from Fusion 360, up to 50 tools — a RepRapFirmware object-model hard limit) and multi-magazine support ("spice racks"/"four packs"); machines can fall back to manual tool change if a slot isn't defined.
- Servo motors are technically supported via RRF but practically limited to CAN-based servos or external drivers; the team recommends NEMA 23 as the practical minimum, citing back-EMF/inductance issues at high RPM with heavy NEMA 23 steppers (48V PSU recommended).
- Spindle power above ~2.2kW is impractical on 110V circuits (common in the US); heaviest real cut reported was 1.8kW (10mm full slot, 8mm 3-flute cutter) — torque has rarely been a real bottleneck versus tool deflection/rigidity/RPM.
- Kata is developing input shaping (motion resonance cancellation) and eventually live spindle-load/vibration monitoring, likely requiring an external RS485 hat or Raspberry Pi since the MCU running RRF can't handle live compensation alone.
- "Fatless" (Phil's project) is a bigger router-style CNC evolution of "Atlas," demonstrating a servo-to-stepper-compatible motor mount design; frame cost estimated ~$1,000 US.
- Filter/enclosure plugin plans include temperature compensation via a chamber thermistor and holding enclosures at a consistent temp (e.g., 30°C) to make thermal expansion predictable rather than actively compensating in real time.
- A touchscreen pendant is planned but blocked waiting on Duet to supply a display unit.

## Details worth keeping
- Print settings: three tiers now documented — aesthetic, semi-structural, structural (e.g., decorative shrouds print in aesthetic mode, ~200-300g).
- Servo example: Phil's Fatless X-axis uses a ~60mm/NEMA-23-equivalent servo; Yanu's Fatless build runs a single 400W servo (~780N force) with 1610 ball screw, theoretical rapids up to ~15 m/s.
- "Ben CNC" is the team's benchy-equivalent test part (circle/diamond/square/boss geometry) for validating machine accuracy, designed to cut from 50mm square stock.
- Fourth-axis rotary centerline height noted as 62.5mm from base — relevant for anyone designing a tailstock/steady rest adapter.
- Servo controllers mentioned as alternative: Masso controller (~$1,000-1,500 USD with touchscreen) used by "Alex Trevor."
- No steady rest/tailstock product yet for the fourth axis; a steady rest is seen as easier but limits work to round stock.

## Skip it if
Skip this if you want a tutorial, spec sheet, or buying guide — there's no step-by-step instruction here, just a casual status-update conversation for people already following the Milo/Miley/Atlas project closely.
