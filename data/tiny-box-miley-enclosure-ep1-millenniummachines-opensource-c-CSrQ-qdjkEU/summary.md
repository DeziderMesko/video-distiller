# Summary: Tiny Box Miley Enclosure Ep1 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=CSrQ-qdjkEU

---

The text checks out — all proper nouns (Millennium Machines, Miley/Milo, CASA, Cascade, RepRapFirmware/Klipper/Marlin, Duet3D, Expatria, West3D, Carvera, Fusion 360, OnShape, Wera, Voron, LinuxCNC) match their standard real-world spellings, and the Miley/Milo distinction is intentional (the host's personal machine nickname vs. the product line), consistent with prior sessions. No corrections needed — returning unchanged.

## TL;DR
This is a casual Millennium Machines livestream, not a tutorial. The host spends most of the two-hour session drilling and tapping 2020 extrusion to start "Tiny Box," a shrunk-down version of the team's CASA enclosure sized to fit their Miley CNC machine rather than the full-size Milo. Interwoven with the build is running commentary on the same-day launch of Cascade (a new Voron-style desktop CNC), a comparison of RepRapFirmware vs. Klipper vs. Marlin, and shop-life banter (calipers, AI use, the dog, food). Anyone wanting hands-on CAD/build steps will get some, but a large fraction of runtime is chat and asides.

## Key points
- The build is "Tiny Box": a condensed CASA-style enclosure (~758 mm wide) sized to fit the Miley CNC rather than full CASA's ~1–1.1 m, since the host now has Atlas as their main machine and just wants a dedicated Miley/4th-axis box [13:16](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=796s) [1:03:13](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=3793s).
- Extrusion lengths are kept uniform across the design specifically so LDO could offer a kit cheaply — one drilled extrusion length ships lighter and needs fewer SKUs than Voron/old-CASA kits [15:01](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=901s).
- Cascade (a new Voron-family CNC) launched today; a Reddit estimate pegs self-source cost at ~$3k, which the host calls "wildly too expensive" [10:06](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=606s).
- Cascade specs: ~1.2 kW spindle, choice of BTT Sila or Expatria controller boards; host isn't a fan of its small fixed-gantry layout and worries about water-cooled spindle complexity, but hasn't used one so won't fully judge it [18:23](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=1103s) [21:24](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=1284s) [33:25](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2005s).
- Firmware take: RepRapFirmware is the most versatile (3D printing, CNC, lasers, robot arms) but is a jack-of-all-trades; Klipper is excellent but 3D-print-focused with weak CNC support; Marlin is architecturally the most "live"/responsive (like LinuxCNC) but painful to maintain since it must be recompiled [38:33](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2313s) [40:32](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2432s) [41:08](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2468s).
- Claude-assisted ("vibe coded") firmware dev goes noticeably better on RepRapFirmware than on Klipper, per the host [40:14](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2414s).
- Duet3D announced new industrial DIN-rail controllers with Phoenix-style connectors, STM32-based, CAN-networked, supporting closed-loop steppers and servos — exciting but expected to carry industrial pricing [36:08](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2168s) [37:21](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2241s).
- Alan from West3D (on the Millennium Machines team) is currently doing the RepRapFirmware dev work behind Cascade [34:10](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2050s).
- Mid-build the host realizes the 660 mm upright extrusions were never ordered, so only the outer frame gets finished this session — the electronics bay has to wait [32:14](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=1934s).
- Host dislikes Carvera-style machines because their slow material-removal rate (hours per part vs. minutes on a 3D printer) makes them impractical for weekend hobbyist use [49:57](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=2997s) [50:58](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=3058s).
- Longer-term plan: once Atlas and the Miley/Tiny Box rig are both set up, the shop will be at capacity, limiting future dev streams; next personal project under consideration is a one-piece milled flying gantry for the LDO Micron [1:28:37](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=5317s) [1:29:20](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=5360s).
- On AI: personally useful for CAD post-processors and firmware dev, but the host and chat agree the societal effect (cheaper/faster output pushing humans out of the loop) is the real concern, not individual use [1:38:24](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=5904s) [1:41:08](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=6068s).

## Details worth keeping
- Drill bit note: blind Voron-style joints in 2020 extrusion technically need a 5 mm bit, but the host uses 6 mm so Wera hex keys (with their thicker sleeves) fit through more easily [20:18](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=1218s).
- Tiny Box frame uses 700 mm extrusions for most of the frame, plus 660 mm uprights and 140 mm cross-beams — the 660s hadn't been ordered yet as of this stream [15:01](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=901s) [32:14](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=1934s).
- Sizing comparison from chat: a Voron 300–350 mm printer's outer footprint is only ~100 mm larger per side than Tiny Box, so anyone with room for a 300/350 Voron has room for this [1:15:09](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=4509s) (merged chat block).
- The host is evaluating a move from Fusion 360 to OnShape for CAM, partly because AI now makes writing custom post-processors much easier [1:37:36](https://www.youtube.com/watch?v=CSrQ-qdjkEU&t=5856s).

## Skip it if
Skip this if you want a structured CASA/Tiny Box build guide or firmware tutorial — it's a slow-paced livestream VOD dominated by drilling, tapping, and chat banter, with the CAD/firmware/Cascade commentary scattered in as asides rather than a organized walkthrough.
