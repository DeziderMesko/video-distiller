# Summary: LDO Miley V2.0 (full production kit) Ep4 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=-OHCU9msaxs

---

## TL;DR
This is episode 4 of a live-streamed build log from Millennium Machines, assembling the LDO Miley V2.0 (an open-source CNC machine kit, a variant of the Milo V2). The streamer builds out the Y-axis table, bearing blocks and belt/pulley hardware while explaining build steps, flagging kit-quality issues to LDO, and chatting with viewers about hobby-CNC news and unrelated topics. It's a casual, unedited hangout stream rather than a structured tutorial — useful mainly to people already following this specific build.

## Key points
- Milo vs. Miley are the same LDO kit with different C-beam/hole orientation: Miley routes through the top, Milo faces the other way; the kit ships with holes for both.
- LDO's shipping delay is attributed to waiting on developer approval for design changes, and the CNC-machined anti-backlash blocks are being dropped from the initial kit after some users reported tuning trouble (though the streamer says he's had six pairs with no issues).
- Detailed diagnosis of a contactor/inrush-current problem: LDO's dual-purpose AC/DC contactor draws ~15W at idle (vs. ~3W for the contactors he sources in the UK), causing a brief inrush that browns out the board and shows up as a false "motor ground" error; workaround is delaying fan startup, real fix would be a lower-draw contactor or a larger (~45-50W) 24V DIN power supply instead of the stock 30W one.
- He asks viewers to message LDO's vendor channel on the Millennium Discord to show demand, since visible interest is what moves kit production up LDO's priority list.
- LDO's informal estimate at the time: kit ships from China by end of July, arrives at sellers by end of August — he cautions to take that "with a grain of salt" since a similar promise for June slipped.
- Critiques LDO's prototype "bulldog vise": an extra material-rest piece is mechanically coupled to the jaw in a way that blocks the drawer screws, requiring near-full disassembly to remove it; he suggests just extending the fixed jaw instead, similar to how the "Inception" vise handles the same overhang need.
- Describes his own grease-distribution system for the Y-axis rails (part of his "Atlas" side project), letting each axis be greased independently or, optionally, continuously oiled via a sump.
- Walks through the Belleville-washer (conical washer) preload procedure for the leadscrew nut assembly, including what to do if the screw doesn't catch threads within the washers' travel (add a spacer between the two washers).
- Stream cuts short after discovering the pulley grub screws are M4 — not the M3/M5 he expected — a kit inconsistency he flags for LDO; he only had two spare M4 grub screws salvaged from an old kit.
- His own MillenniumOS-based tool-changer firmware ("my homebrew version of MOS") is nearly ready for testing on the ATC side, with the goal of finishing the mechanical build so only minor tuning and covers remain.

## Details worth keeping
- Fasteners used during this session: M5x12/M5x10 for the frame and T-nuts, M3x10 for most sub-assemblies, M3x40 for the compression-plate preload screws, and 0.3mm Belleville washers (a size he specifically requested LDO include in kits).
- Blind-hole butt joints on the C-beam should go on the screw side, not the extrusion side — otherwise the T-nut can get dragged out of position when sliding parts together.
- He recommends against glass-fiber-filled filament (e.g. PETG-GF) for these printed parts, since it throws off sliding fits; plain ASA or ABS is his recommendation.
- Y-axis wire rail length for V2 is roughly 600mm, per his recollection (he wasn't fully certain — check the BOM).
- Expect to lose roughly 10mm of usable Z build height when running a BT30 tool holder at full retraction for ATC.
- Pulley grub screws in this kit turned out to be M4, not the M3/M5 typically expected — worth checking before assembly.

## Skip it if
You're not building or evaluating this specific LDO Miley/Milo V2 kit — the stream is mostly raw build narration interspersed with long unrelated chat (video games, pets, the weather) and has no general CNC-building tutorial value.

Let me know if you'd like me to save this to `summary.md` in that video's folder — I'll need write permission approved for that path.
