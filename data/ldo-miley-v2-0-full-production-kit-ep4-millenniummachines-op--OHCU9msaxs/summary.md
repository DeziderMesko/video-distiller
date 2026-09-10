# Summary: LDO Miley V2.0 (full production kit) Ep4 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=-OHCU9msaxs

---

## TL;DR
This is a Millennium Machines livestream in which the host resumes building a Miley V2 (CNC router) kit from LDO, working through the Y-axis table, compression-plate preload, and pulley installation while fielding chat questions. Along the way he explains why LDO's kits have been delayed (dropped anti-backlash blocks, a power-supply/contactor brownout bug) and asks viewers to lobby LDO directly for faster kits. Roughly half the \~1h50m runtime is unstructured chat banter (gaming, a garage fire he helped with, filament shortages) rather than build content. Useful mainly for people already committed to building a Milo/Miley V2 or following LDO's kit-delivery saga.

## Key points
- LDO dropped the CNC anti-backlash blocks from the initial kit and is also fighting a contactor inrush-current bug that browns out the board (shows up as a false "motor ground" error); firmware now delays fan power-up to work around it [11:43](https://www.youtube.com/watch?v=-OHCU9msaxs&t=703s).
- Fix for the brownout: use a lower-draw contactor (host's UK-sourced one draws \~3W vs LDO's \~15W idle) or a bigger DIN power supply (45-50W instead of 30W) [16:05](https://www.youtube.com/watch?v=-OHCU9msaxs&t=965s).
- Host asks viewers who want kits sooner to post in the LDO vendors channel on the Millennium Machines Discord, politely asking about the holdup — visible demand moves LDO's priorities [17:05](https://www.youtube.com/watch?v=-OHCU9msaxs&t=1025s).
- LDO told him kits should ship from China end of July, ready at sellers by end of August — he explicitly says take that with a grain of salt since a June date already slipped [54:57](https://www.youtube.com/watch?v=-OHCU9msaxs&t=3297s).
- Compression-plate preload technique: stack two 0.3mm Belleville (conical) washers cone-to-cone, tighten evenly in a diamond pattern, then back off a quarter-turn at a time per corner until the leadscrew nut thread just catches; if it never catches, add a spacer between the washers to shift the engagement point [39:12](https://www.youtube.com/watch?v=-OHCU9msaxs&t=2352s), [42:41](https://www.youtube.com/watch?v=-OHCU9msaxs&t=2561s), [46:39](https://www.youtube.com/watch?v=-OHCU9msaxs&t=2799s).
- LDO's new pulleys use a non-standard (M4) grub screw size that doesn't match the M3/M5 hardware in the rest of the kit or older LDO rings — a build snag he says he'll report to LDO [1:40:16](https://www.youtube.com/watch?v=-OHCU9msaxs&t=6016s), [1:47:16](https://www.youtube.com/watch?v=-OHCU9msaxs&t=6436s).
- V2's Y-axis is 200mm longer than V1.5's — described as a significant usable-space upgrade [20:31](https://www.youtube.com/watch?v=-OHCU9msaxs&t=1231s).
- Milo vs. Miley are the same V2 platform built two ways: Milo has the C-beam facing one way through the top, Miley the other way, using different pre-drilled holes on the same kit [7:28](https://www.youtube.com/watch?v=-OHCU9msaxs&t=448s).
- Critiques LDO's prototype "bulldog vise": good split-jaw concept, but a mechanically-coupled front ledge piece blocks the drawer screws, requiring a multi-step teardown just to remove the drawer [21:09](https://www.youtube.com/watch?v=-OHCU9msaxs&t=1269s).
- On the software side, his own homebrew firmware/CAM stack for the ATC is basically ready to test; separately, a community member ("Nine") has closed-loop control working on NEMA17 motors under RepRapFirmware 3.7, pending an official merged config image [6:18](https://www.youtube.com/watch?v=-OHCU9msaxs&t=378s), [1:00:48](https://www.youtube.com/watch?v=-OHCU9msaxs&t=3648s).

## Details worth keeping
- Ran out of PETG-GF filament (finally, gladly) and is switching to ABS-GF (\~10kg incoming) for future prints — he no longer wants to use glass-fiber-filled material because it ruins sliding-fit tolerances [31:49](https://www.youtube.com/watch?v=-OHCU9msaxs&t=1909s).
- Separately ran short on Prusament PC-CF mid-assembly (last ring on the spool); waiting on a resupply from a contact ("Tommy") before finishing the missing panels, otherwise will substitute ABS-GF [54:57](https://www.youtube.com/watch?v=-OHCU9msaxs&t=3297s).
- Grease port design note: the CNC'd part is drilled from two directions and sealed with a grub screw to form the internal grease channel — same principle used in his in-development independent per-axis (or optional sump) grease system for his own "Atlas" machine [25:06](https://www.youtube.com/watch?v=-OHCU9msaxs&t=1506s).
- Saunders Machine Works (SMW) also makes plates for other hobby CNC machines (Shapeoko, DMT Mini/DMC2) [18:19](https://www.youtube.com/watch?v=-OHCU9msaxs&t=1099s).
- Personal aside: helped evacuate an elderly neighbor during a garage fire a few doors from his flat [48:41](https://www.youtube.com/watch?v=-OHCU9msaxs&t=2921s).

## Skip it if
You're not already invested in Millennium Machines' Milo/Miley V2 kit or LDO's supply situation — there's no general CNC tutorial value here, and a large chunk of the stream is off-topic chat (gaming, personal life) rather than build instruction.
