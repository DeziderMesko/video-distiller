# Summary: Millennium Electronics Box : Ep 2 #3dprinting #millenniummachines #opensource #filament #cncmachine

Source: https://www.youtube.com/watch?v=IVJy6Z1uSsQ

---

## TL;DR
A livestream (not a tutorial) from Millennium Machine Works, building an electronics enclosure ("Casa") for the Milo CNC machine — drilling ACM panels, threading bolts, sorting out wiring/DIN rail layout. Most of the runtime is the host chatting with viewers about channel direction (more project videos vs. streams), other Millennium projects in progress (ATC modules, 4th axis, Micron), and personal life (possibly moving for an engineering job, van life plans). Very little of it is instructional CNC content — it's a hangout stream with a build happening in the background.

## Key points
- Building an electronics box ("Casa") for the Milo CNC machine: ACM side panels drilled and fitted, feet and handles added, back panel has cable grommets and keystone jacks (planned I/O: 1x Ethernet + 1x USB on back, 1x USB + 1x HDMI on front) for an internal Raspberry Pi.
- Design was inspired by Rat Rig's electronics box but reworked to be smaller with better internal layout; open-source credit will be given to Rat Rig in the manuals.
- Host plans to shift content strategy toward more project-based YouTube videos and fewer/weekly streams, since videos (not streams) drive channel growth/subscribers — cites a recent tramming tutorial video as their best-performing non-announcement video.
- Product/roadmap updates: automatic tool changer (ATC) "four pack" and "spice rack" modules — hardware is done and tested, but tool-change automation is blocked on one developer (Nine Mile) who's a new parent and short on time; software integration (servo timing, lid open/close, G-code hooks) is the remaining work.
- A 4th axis is in development (by "Phil"); hardware will take longer than software since Fusion 360's 4th-axis CAM is a paid feature, which has slowed their own progress.
- A fixed-gantry machine called "Atlas" (moving table in Y, moving spindle in Z/X) is planned as a successor project, but the host is explicit that burnout is a real risk and they can't promise Atlas will ship or that they'll stay on the project a year from now.
- Practical CNC tips mentioned in passing: cutting ACM drills more cleanly than acrylic; steel chip color (brownish/straw) indicates tempering heat during machining; flood coolant is strongly preferred over mist coolant due to cancer risk from inhaling atomized coolant.
- Personal: host may be relocating for their first engineering job; considering converting a box truck into a live-in van (raised floor for underfloor storage, workshop area for Milo + a 3D printer) and renting out their current house to cover costs.
- Host discusses ADHD diagnosis (made outside the UK, not recognized by the NHS, ~5-year wait to get retested/diagnosed there) and general reflections on the CNC/3D-printing hobby community skewing older.

## Details worth keeping
- Panel hole spacing referenced during the build: 13mm edge-to-edge and 10mm edge-to-edge (rough field measurements, not a finalized spec).
- Bolt sizing: M5x10 was too short; M5x12 needed for the panel/handle mounts.
- I/O plan for the box: Ethernet + USB (rear), USB + HDMI (front), keystone jacks for modularity.
- Caveat: this is a livestream chat log, not a tutorial — no step-by-step instructions or final wiring were completed on stream (DIN rail wiring was deferred to next time).

## Skip it if
You want a tutorial on building the electronics enclosure or wiring the Milo — none of that actually happens here. Skip unless you're specifically interested in Millennium Machine Works community/roadmap chatter or the host's personal life updates.
