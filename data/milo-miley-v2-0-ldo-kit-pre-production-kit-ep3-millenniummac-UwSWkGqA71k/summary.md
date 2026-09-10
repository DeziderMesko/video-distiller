# Summary: Milo/Miley V2.0 LDO Kit Pre production kit Ep3 #millenniummachines #opensource  #cncmachine

Source: https://www.youtube.com/watch?v=UwSWkGqA71k

---

## TL;DR
This is Episode 3 of a Millennium Machines livestream (with co-host Hans) building the LDO pre-production kit for the Milo/Miley V2.0 CNC router — mostly hands-on assembly of the Y-axis anti-backlash nuts, rail carriages, and lead screws, interspersed with a lot of off-topic chat (Star Trek, Red Dwarf, pets, merch plans). The most useful content is troubleshooting LDO's incorrect washer substitution, a demonstrated technique for squaring linear rail carriages without a dial indicator, and background on the Milo/Miley/Atlas machine family and their RepRap-Firmware-based "MOS" software stack. It's a working-build VOD, not a tutorial video — expect a manual-free, error-and-correct-live pace.

## Key points
- The C-beam extrusion Milo uses only fits small (0802) ball screws with a 2mm lead, so multi-flute tooling feed rates hit stepper RPM limits — that's why V2 specs TR8 lead screws instead of ball screws by default; the upcoming Atlas design uses bigger 1204/1210 ball screws, which only halve (not quarter) the feed rate versus lead screws [6:45](https://www.youtube.com/watch?v=UwSWkGqA71k&t=405s).
- LDO shipped wave spring washers instead of the specified conical (Belleville) disc washers for the anti-backlash nuts; the wave washers have since flattened out under load and lost their spring, unlike conical washers which spread load across the full radius [5:28](https://www.youtube.com/watch?v=UwSWkGqA71k&t=328s) [35:33](https://www.youtube.com/watch?v=UwSWkGqA71k&t=2133s).
- Correct stacking method for conical/Belleville washers: cone tips face each other with a gap in the middle, and the outer brass insert backs the washer edge so it can't bite into the printed plastic [33:52](https://www.youtube.com/watch?v=UwSWkGqA71k&t=2032s).
- In testing, a well-tuned anti-backlash nut gave backlash roughly comparable to cheap AliExpress (\~C10 grade) ball screws; Hans's C5-ground 1210 ball screws performed noticeably better [10:55](https://www.youtube.com/watch?v=UwSWkGqA71k&t=655s).
- Demonstrated rail-carriage "tramming" technique: press dial pins against both sides of a carriage, lightly snug M5 countersunk screws in a star pattern to wedge the pins against the carriage, then tighten the carriage down — no indicator needed. Must be done on at least two carriages per rail, not just one, or the other rail can bind [57:02](https://www.youtube.com/watch?v=UwSWkGqA71k&t=3422s) [1:09:44](https://www.youtube.com/watch?v=UwSWkGqA71k&t=4184s) [2:06:00](https://www.youtube.com/watch?v=UwSWkGqA71k&t=7560s).
- Milo/Miley run RepRap Firmware (RRF) plus "MOS" (Millennium Operations System), a setup-wizard/macro package built by community member "Nine Mile" (real name Ben) that adds CNC probing cycles and a 4th-axis; the BigTreeTech "Scylla" board was co-designed specifically for Milo, and MOS works on any RRF-compatible board including PrintNC and Shapeoko [1:40:08](https://www.youtube.com/watch?v=UwSWkGqA71k&t=6008s) [1:45:05](https://www.youtube.com/watch?v=UwSWkGqA71k&t=6305s).
- Host criticizes Elegoo for building the Centauri Carbon on Klipper while rebranding it and not releasing required source files, calling it a clear Klipper license violation [1:18:52](https://www.youtube.com/watch?v=UwSWkGqA71k&t=4732s).
- Atlas (a larger CNC in development) needs thick-wall (5mm) 40-series extrusions to allow blind joints, unlike standard 2-3mm Bosch-style extrusion; it will reuse the same double-size fixture/bed plate as Milo/Miley to cut manufacturing cost [20:46](https://www.youtube.com/watch?v=UwSWkGqA71k&t=1246s).
- Miley moves only the fixture plate (310mm X travel) while Milo moves the whole table (350mm X); Miley's enclosure can be \~200mm shorter, Milo has more room for accessories [2:08:59](https://www.youtube.com/watch?v=UwSWkGqA71k&t=7739s).
- Y-axis assembly finished this stream; X-axis planned as a solo stream next, then Z-axis together with Hans — LDO is waiting on this feedback before kits ship, though tracking numbers for the pre-production test kits have already gone out [2:22:57](https://www.youtube.com/watch?v=UwSWkGqA71k&t=8577s) [2:24:56](https://www.youtube.com/watch?v=UwSWkGqA71k&t=8696s).
- Host is exploring Millennium Machines merch (t-shirts/hoodies) via Square's print-on-demand-style drop-shipping so no stock needs to be held; prefers Square over Shopify and Odoo for ease of payments/VAT handling [1:00:43](https://www.youtube.com/watch?v=UwSWkGqA71k&t=3643s) [1:03:52](https://www.youtube.com/watch?v=UwSWkGqA71k&t=3832s).
- Host criticizes PrintNC's use of dual ball screws cantilevered off a thin tube, arguing it will rack out of tram over time — calls it a router, not a mill [1:38:15](https://www.youtube.com/watch?v=UwSWkGqA71k&t=5895s).

## Details worth keeping
- Belleville washers, "disc springs" and "conical washers" are all the same part — interchangeable terminology used throughout [1:30:36](https://www.youtube.com/watch?v=UwSWkGqA71k&t=5436s).
- If you can't source the correct washers, LDO anti-backlash nuts can still be run V1.5-style: just mechanically compress with the four screws and skip the spring-washer stack entirely [1:30:36](https://www.youtube.com/watch?v=UwSWkGqA71k&t=5436s).
- Bright (writing the build manual) suggested an alternate tramming method using the Z-axis shoulder bolts on one side instead of a second set of countersunk pins — host confirms it's an acceptable substitute [56:44](https://www.youtube.com/watch?v=UwSWkGqA71k&t=3404s).
- Mobile workbench cost breakdown the host is planning: two Kallax units (\~£50 each), two sheets of plywood (\~£35 each), casters (\~£30) — total \~£200-250 [1:55:27](https://www.youtube.com/watch?v=UwSWkGqA71k&t=6927s).
- LinuxCNC is described as excellent but not beginner-friendly: "if you've ever struggled to install Klipper, forget about LinuxCNC" [1:16:16](https://www.youtube.com/watch?v=UwSWkGqA71k&t=4576s).
- Channel isn't monetized yet — needs 3,000 watch hours, was around 2,000-something at time of recording [1:27:45](https://www.youtube.com/watch?v=UwSWkGqA71k&t=5265s).

## Skip it if
You're not actively building a Milo/Miley V2 CNC kit or following LDO's kit QA process — most of the runtime is real-time assembly troubleshooting and unrelated banter (Star Trek/Red Dwarf chat, pet antics, personal updates) rather than a structured tutorial.
