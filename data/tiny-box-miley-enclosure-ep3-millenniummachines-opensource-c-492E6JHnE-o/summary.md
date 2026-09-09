# Summary: Tiny Box Miley Enclosure Ep3 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=492E6JHnE-o

---

## TL;DR
This is a ~2h15m Millennium Machines live-build stream in which the host works through CAD and physical prototyping for "Casita," the electronics enclosure for **Miley**, the smaller variant of the open-source **Milo** CNC router (Casita is the small-enclosure counterpart to the full-size **Casa** enclosure). Substantive content covers a new printed DIN-rail backer plate with a self-tapping fastening slot, an airflow/overpressure cooling design with optional coolant-mist filtration, a filtered vent panel, and spindle/power-supply component decisions, all demonstrated live with test prints and fit checks. A large share of runtime is unstructured chat banter (3D printer brands, anime, personal updates), so it's best suited to people already following the Milo/Casita build rather than anyone wanting a tight tutorial.

## Key points
- New printed DIN-rail backer plates for Casita replace the old unsupported rail span; they use a "speed groove" — a slot with steps spaced 0.8mm apart (matching M5 thread pitch, 4.2mm minor-diameter hole) — so a self-tapping M5 screw can seat anywhere along the slot regardless of where a given DIN rail's mounting cutouts fall [8:16](https://www.youtube.com/watch?v=492E6JHnE-o&t=496s).
- Demonstrated result: screwing the DIN rail into the backer plate at mid-span (using the speed groove) eliminates the flex that plagued the old design — described as "night and day" more rigid [1:56:36](https://www.youtube.com/watch?v=492E6JHnE-o&t=6996s).
- Airflow design pushes cool air through the electronics bay into the main chamber, creating overpressure; if running coolant, that requires a drip tray plus a three-stage filter down to HEPA before venting, since atomized coolant mist is dangerous to breathe (and to pets) — skip the filter train entirely if not running coolant [19:23](https://www.youtube.com/watch?v=492E6JHnE-o&t=1163s), [19:34](https://www.youtube.com/watch?v=492E6JHnE-o&t=1174s).
- A new printed vent panel uses gyroid infill as the actual filter media plus a TPU gasket and an internal deflector, so outside air can pass into/out of the electronics bay without the chips or dust reaching the electronics [15:30](https://www.youtube.com/watch?v=492E6JHnE-o&t=930s).
- Structural parts are designed around plain ABS tolerances; when printed in glass-fiber ABS (used for its look/rigidity) they warp and fit tight/undersized, requiring extra clearance or manual sanding — a recurring fit problem during the stream's test-fitting [32:43](https://www.youtube.com/watch?v=492E6JHnE-o&t=1963s), [1:44:57](https://www.youtube.com/watch?v=492E6JHnE-o&t=6297s).
- Spindle guidance: never run an air-cooled spindle below 50% speed (~12k RPM on common budget spindles) for more than a few minutes or it cooks the bearings; water-cooled spindles avoid that constraint and, once bearing quality (tapered roller, not plain ball) is matched, are often cheaper than a comparable air-cooled unit — LDO kit spindles are cited as having correct bearings [42:07](https://www.youtube.com/watch?v=492E6JHnE-o&t=2527s), [48:04](https://www.youtube.com/watch?v=492E6JHnE-o&t=2884s).
- The Milo/Casa extrusion frame layout is locked in through at least "V2.3" with no further extrusion changes planned; a future monobody (single solid piece) frame option will be offered alongside the current split-body design [44:02](https://www.youtube.com/watch?v=492E6JHnE-o&t=2642s).
- Casita's panel size is capped by the need to fit on a standard 250mm 3D-printer build plate, which is the main constraint driving the cramped electronics-bay layout [20:48](https://www.youtube.com/watch?v=492E6JHnE-o&t=1248s).
- A US-market C20 IEC power inlet (not the UK-typical C13) is required in the enclosure because of the current draw of a 2.2kW spindle at US mains voltage [2:07:46](https://www.youtube.com/watch?v=492E6JHnE-o&t=7666s).
- Planned HMI: an old, cracked-screen Samsung Galaxy S21 will be DIN-mounted inside and run via Samsung DeX as a lightweight touchscreen interface, powered off an independent port so it stays charged without needing the main enclosure power cycled [2:09:52](https://www.youtube.com/watch?v=492E6JHnE-o&t=7792s), [2:18:01](https://www.youtube.com/watch?v=492E6JHnE-o&t=8281s).

## Details worth keeping
- Thread math for self-tapping DIN screw holes: subtract the thread pitch from the major diameter to get pilot-hole size (M5 → 4.2mm hole) [8:53](https://www.youtube.com/watch?v=492E6JHnE-o&t=533s).
- USB front-panel cutouts were a poor fit not because of a design error but because the injection-molded USB parts are lower tolerance than the Ethernet ones — light sanding/filing fixes the fit [15:38](https://www.youtube.com/watch?v=492E6JHnE-o&t=938s).
- Plywood-enclosure durability hack: coat with truck-bed liner spray ("Raptor Liner"/Raptor paint) — cheap, textured, scratch-resistant, and used successfully on the host's original FMJ builds [34:48](https://www.youtube.com/watch?v=492E6JHnE-o&t=2088s).
- Host reached out to Creality about getting their M1 filament recycler for scrap ABS/PLA reuse; no response as of this stream [29:55](https://www.youtube.com/watch?v=492E6JHnE-o&t=1795s).
- Bambu Lab was reportedly out of stock on glass-filled black ABS until end of June (supply constrained by import/petrochemical issues); host had only one spool left going into this build, a real risk to finishing the enclosure in that material [55:11](https://www.youtube.com/watch?v=492E6JHnE-o&t=3311s).
- A partial-depth heat-set-insert technique (learned on the "Micron" build): mirror a partial-depth insert hole on two adjoining plates so a single insert fuses them into one piece when installed [11:51](https://www.youtube.com/watch?v=492E6JHnE-o&t=711s).

## Skip it if
You want a concise CNC-enclosure tutorial or aren't already following the Milo/Miley/Casita open-source project — most of the runtime is live improvisation, test-fit troubleshooting, and off-topic live-chat conversation (3D printer brands, anime, personal life updates) rather than a structured walkthrough.
