# Summary: Tiny Box Miley Enclosure Ep4 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=r8if4N5xRW4

---

## TL;DR
This is a casual Millennium Machines (open-source CNC mill project — Milo/Miley) dev livestream. The host builds out the compact "Casita" electronics enclosure (successor to the bulkier "Casa") while chatting with guest Phil, a team developer building his own high-spec personal machine codenamed FATLAS. Substantive content is scattered between build progress and long stretches of banter: LDO kit sourcing/BOM decisions, CNC workholding and coolant practice, and a rundown of CNC firmware/UI ecosystems (RepRapFirmware/Duet vs. GRBL-HAL vs. LinuxCNC). It's a hangout stream, not a tutorial — useful mainly to people already following this specific project.

## Key points
- The upcoming LDO V2 kit will be identical for Milo and Miley (same extrusions/fasteners, machines differ only in printed parts; Miley needs an extra belt and two pulleys); no ship date or price is set yet [33:19](https://www.youtube.com/watch?v=r8if4N5xRW4&t=1999s).
- That kit round will **not** include end mills — carbide costs have spiked sharply, especially sourced from China — so buyers need to source their own; team member Dave (Desktop Machine Shop) still sells them while stock lasts [36:48](https://www.youtube.com/watch?v=r8if4N5xRW4&t=2208s).
- Enclosure electronics are being split out of the base kit entirely into a separate "Universal Electronics Box" (UAB); the base V2 kit only ships machine-specific electronics (motors, end stops, VFD/spindle) [35:07](https://www.youtube.com/watch?v=r8if4N5xRW4&t=2107s).
- Tape-and-glue workholding tips: it's \~99% surface prep — clean thoroughly with acetone (dries faster/cleaner than IPA or drugstore-grade acetone), keep coolant off taped surfaces entirely, and use dry air blast only while cutting taped parts [40:35](https://www.youtube.com/watch?v=r8if4N5xRW4&t=2435s).
- The host is redesigning the electronics enclosure as "Casita," a smaller, cheaper version of "Casa," including a magnetically-mounted blank distribution panel users can fit with their own connectors (aviation, Phoenix, or screw-terminal) [6:39](https://www.youtube.com/watch?v=r8if4N5xRW4&t=399s).
- Guest Phil's personal project, codenamed FATLAS, runs EtherCAT servo motion, HGR20-class linear rails, and 1610 ball screws on heavy-wall 4040 extrusion, with a (sic) "Junkin" ISO20 ATC spindle (2.2 kW, 24,000 RPM, \~€1,400); whether it becomes an official Millennium Machines design is still undecided [27:37](https://www.youtube.com/watch?v=r8if4N5xRW4&t=1657s), [57:35](https://www.youtube.com/watch?v=r8if4N5xRW4&t=3455s).
- Firmware/UI explainer: RepRapFirmware + Duet Web Control bundle motion control and UI together as one package; GRBL-HAL/FluidNC only handle G-code execution and need a separate sender/UI (Universal G-code Sender, ncSender); LinuxCNC similarly supports many interchangeable front ends (QtDragon, gmoccapy, etc.) [1:30:48](https://www.youtube.com/watch?v=r8if4N5xRW4&t=5448s).
- Fusion 360 tips: pressing Space repeats the last operation (e.g. re-chamfering without reselecting the toolbar), and a single chamfer operation can mix different chamfer sizes via its "+" button for a second edge selection [20:16](https://www.youtube.com/watch?v=r8if4N5xRW4&t=1216s), [20:57](https://www.youtube.com/watch?v=r8if4N5xRW4&t=1257s).
- Mounting a camera directly to a spindle picks up too much vibration (and previously caused EMI issues feeding into OBS); both host and Phil instead use a cheap articulating microphone arm with a GoPro adapter [1:12:05](https://www.youtube.com/watch?v=r8if4N5xRW4&t=4325s).

## Details worth keeping
- Casita enclosure depth: 700 mm (750 mm including panel width), 100 mm less than Casa [29:50](https://www.youtube.com/watch?v=r8if4N5xRW4&t=1790s).
- Casita's DIN-rail "speed slot" mount fixes an old problem where components (like the VFD) flopped around on standard DIN rail [1:00:03](https://www.youtube.com/watch?v=r8if4N5xRW4&t=3603s).
- Wi-Fi/Sila antenna placement: mount away from anything metallic (top panel, not extrusion); always unplug the ESP antenna cable before removing that panel or you'll rip the connector off [51:12](https://www.youtube.com/watch?v=r8if4N5xRW4&t=3072s).
- Coolant guidance for Milo: WD-40/kerosene-based fluids suit aluminum; avoid IPA near steel cutting (sparks + flammable mist); water-miscible shop coolants (\~1:10 dilution) are a solid hobbyist default; deionized water works but will rust unprotected parts unless greased [2:10:03](https://www.youtube.com/watch?v=r8if4N5xRW4&t=7803s).

## Skip it if
You're not following the Millennium Machines/Milo project specifically — there's no general CNC tutorial content here, just project-specific build updates and long off-topic chat (Patreon numbers, German May Day traditions, personal stories).
