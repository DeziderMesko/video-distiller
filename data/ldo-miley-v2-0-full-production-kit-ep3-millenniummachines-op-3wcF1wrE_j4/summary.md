# Summary: LDO Miley V2.0 (full production kit) Ep3 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=3wcF1wrE_j4

---

## TL;DR
This is a low-key Sunday livestream (Ep3 of a build-log series) from the Millennium Machine Works channel owner, assembling their personal Milo CNC ("Miley") from the LDO V2.0 full production kit. The technical content is limited to mounting the Y-axis motor plate and the Z-axis plate — side panels, way covers and final rail alignment are deferred. Roughly half the 88 minutes is casual chat with viewers (weather, life updates, unrelated banter) rather than build content, interspersed with commentary on the "Moss" control-software UI work the host is doing in parallel.

## Key points
- Build scope for this session: mount the Y-axis motor and plate, check bearings, assemble the Z-axis plate. Way covers, side hold-downs, and rail alignment are explicitly left for later — this is only ~1/3 of the remaining physical build.
- Critical assembly caveat: the drive pin connecting the motor coupling to the drive nut must be installed, or the anti-backlash nut can skew — the host forgot it twice on stream while assembling the Y-axis.
- Upgrade guidance for Milo parts: printed parts perform well in compression (motor/bearing mounts are fine printed), but anything bending/in tension — side plates, XY plates, the frame — is a poor candidate for printing. The best CNC-metal upgrade targets named are the X motor mount/bearing block (it also acts as a torsional bed stiffener) and the Z-axis "sword/hilt assembly" mounting part.
- The host criticizes a third-party CNC'd parts kit for the older V1.5 Milo for adding "speed holes" (lightening holes) to metal parts — pointless on rigid CNC parts (lightening only matters for fast-moving printed parts) and it made the parts more expensive since removing material costs more machining time.
- Coolant/lubricant notes: IPA, WD-40, and kerosene-based fluids all work on aluminium but are flammable (outdoor/ventilated use only); alcohol- and WD-40-based fluids strip grease from linear rails over time, so re-grease monthly or oil before each use if using them. ABS is not chemically resistant to all coolants — test compatibility first.
- Rail alignment method shown: no dial indicator — tighten rail-mounting bolts progressively (two at a time) while running the carriage back and forth by hand/drill to feel for binding.
- LDO kit status: the earlier concern about mis-drilled extrusion holes is resolved; everything else in the kit has been "up to pretty good standards." The host expects the kit's public release to slip past the originally announced date but not by much.
- Parallel software work on "Moss" (the Milo control UI): adding a basic ops page (drilling/facing ops, possibly stock-squaring), configurable RGB status lighting (idle/homing/tool-change states), and the ability to review/rerun individual setup-wizard steps instead of the whole wizard. A collaborator, Cade, is separately building an NXT tool-table feature the host wants to fold into Moss; "NXT" itself (a next-gen product) is still well off.
- Plan for future sessions: finish rail alignment off-stream, then a session dedicated to the X-axis (built as one assembly), then final mounting into the Miley frame — possibly swapping the supplied LDO test motors for Oznest motors (10m cables on hand) if wiring length is insufficient.

## Details worth keeping
- Hardware used in this session: mostly M3×10 and M3×40 screws (M3×40 only for the printed-version AB block, not the CNC version — CNC version uses M3×10 throughout except bellow-plate screws), M5×12 cap screws for the XY joiner plate, M5×15 for a motor-mount step, M3×20 with M3 washers.
- Explicit safety point: never run alcohol/WD-40/kerosene-based coolants indoors.
- No new information on the UEB-to-machine cable length (a standing open question from earlier research).

## Skip it if
You want efficient, distilled build instructions — the actual assembly content is thin relative to runtime, and most of it (short of the drive-pin/coolant/upgrade tips above) is livestream banter with chat. Better suited to someone following the series for the ongoing narrative or curious about the Moss software roadmap.
