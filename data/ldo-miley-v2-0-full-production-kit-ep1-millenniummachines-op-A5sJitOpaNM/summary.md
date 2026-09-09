# Summary: LDO Miley V2.0 (full production kit) Ep1 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=A5sJitOpaNM

---

## TL;DR
This is a ~3-hour live-build stream from Millennium Machine Works, in which the host begins assembling an LDO-sourced kit for Miley V2.0 (the "table stays still, gantry moves" variant of the Milo CNC router), following LDO's manual for the first time. The session covers Z-axis assembly only — printed parts, heat-set inserts, anti-backlash nut preload/tuning, and frame squaring — interspersed with a long guest chat with Alan from West3D (a US Voron/CNC dealer) about kit issues, filament materials, trade shows, and the broader 3D-printing/CNC hobby scene. It's a build-log/community-hangout stream, not a tutorial video — useful mainly for people actually building this specific kit or following the project's development.

## Key points
- **Z-axis assembly completed** (frame extrusions, floating bearing boxes, AB bearing blocks, anti-backlash nut preload, motor mount); rails, motor wiring, and Z-plates deferred to future streams. Y-axis planned next.
- **Anti-backlash nut tuning walkthrough**: compress Belleville (conical) washers in a star pattern until the lead-screw nut threads align, then back off opposing corners a couple of turns to preload; verify by checking it spins freely at low drill torque (1–5 setting).
- **LDO has been iterating on Millennium's original printed-part design** based on real-world build feedback: milled anti-backlash blocks now have 8 compression-plate holes instead of 4 (to help align lead-screw nut starts), plus optional 0.5mm washer shims for finer preload adjustment — LDO's changes are being fed back into the official design.
- **Minor known kit issues** reported to LDO: mainboard (Sila) ships some connectors as bare wire/ferrules rather than JST as expected, and bellows need extra VHB tape since LDO's bellows lack end caps (would prevent full compression).
- **Print settings**: parts are split into semi-structural, structural, and aesthetic (aesthetic still has 3 perimeters, not just 2); LDO kit uses Voron-spec M3 heat inserts (host personally prefers CNC Kitchen-spec); lead-screw version is the standard build for the LDO kit (ball-screw exists but only makes sense with servos).
- **LDO kit pre-orders**: still no firm date; team was told "by end of this month" but dates are explicitly caveated as unreliable and subject to slip if issues are found. Rough pricing is known but not stated on stream.
- **Design philosophy discussion** (with Alan/West3D): fully-printed spindle mounts are being phased out in favor of milled mounts once available, since printing them cost ~1kg filament and ~8–12 hours per part just to then be discarded; Atlas (the host's next project) will integrate the LDO-style milled mount natively.
- **Materials segment**: PPS-CF (HDT ~260°C) and PPA-CF (HDT ~220°C, very stiff vs ABS) are being tested by West3D's Ambrosia filament line; glass-fiber fill dampens vibration roughly 2x better than carbon-fiber fill (better for CNC parts), while CF is lighter and more impact-resistant.
- **Trade show commentary**: MRRF (referred to phonetically as "Smurf"/"Murph" in the transcript) cost the UK team ~£1,000 for a "silver membership" last year, with poor booth placement hurting foot traffic; organizers are stepping back and the event's future format is uncertain. Other US shows discussed: Rocky Mountain RepRap Festival (free, Voron-heavy, host's favorite), 3D Printopia (moving to Philadelphia), Open Sauce.
- Host is now an authorized Prusa reseller (via West3D) despite never having owned a Prusa printer; praises the Prusa Core One and Prusa Connect workflow over Bambu Lab's software, which he criticizes for frequent login/plugin interruptions.

## Details worth keeping
- Fastener spec for this section: M3×10 for most anti-backlash block screws, M5×10 for T-nuts into extrusion slots, M5×12 for screws into extrusion ends, M5×65/M5×60 for the Z motor mount.
- Belleville washers = conical/semi-plane compression washers; stack them dished-side facing each other to create the preload gap.
- Recommend a long-handled M5 Allen key for this build.
- Milo vs. Miley: identical kit, only 3 differing parts (a belt + two pulleys) determine whether the bed or the gantry moves in X.
- Referenced elsewhere: a separate tramming guide video exists on the same channel for squaring a completed Milo/Miley.
- West3D (Portland, OR) is the recommended US vendor for this kit; no direct-from-LDO consumer sales.

## Skip it if
You're not actively building (or specifically deciding whether to build) the LDO Milo/Miley V2 kit — there's no general CNC or 3D-printing tutorial content here, and roughly half the runtime is off-topic chat about filament brands, trade shows, and pets.
