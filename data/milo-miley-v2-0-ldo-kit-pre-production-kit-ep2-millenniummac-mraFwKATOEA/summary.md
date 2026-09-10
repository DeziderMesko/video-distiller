# Summary: Milo/Miley V2.0 LDO Kit Pre production kit Ep2 #millenniummachines #opensource  #cncmachine

Source: https://www.youtube.com/watch?v=mraFwKATOEA

---

Nothing in the text needs correction — cross-checking against saved project memory confirms "Milo" (the Millennium Machines CNC) and "Miley" (the host's personal nickname for their own build) are both accurate as written, not ASR mishearings, and terms like LDO, Voron, Klicky/Tap/Beacon/BTT Eddy, Blanchard ground, Belleville, and Bambu A1 Mini are all legitimate real-world names already rendered correctly.

## TL;DR
This is a ~2-hour co-working/live-build stream for the Milo/Miley V2.0 CNC mill kit (parts supplied by LDO), hosted by the machine's designer (addressed on stream as Jake) alongside co-builder Hans, with heavy Discord chat interspersed throughout. Genuine build content — heat-inserts, motor mounts, anti-backlash lead-screw nut assemblies, floating bearing blocks — is scattered between long stretches of banter, but the stream does surface a real kit defect (wrong washer type from LDO) and some design-philosophy and project-roadmap news. Anyone not actively assembling this specific kit will get little out of it.

## Key points
- LDO's kit defect found live: the anti-backlash nut assembly is spec'd for conical/Belleville spring washers, but LDO shipped wave washers instead, which don't stack correctly and don't give proper preload — Jake asks the community to get LDO's documentation corrected and says he may pause his own build if it doesn't work out. [1:48:34](https://www.youtube.com/watch?v=mraFwKATOEA&t=6514s)[1:57:15](https://www.youtube.com/watch?v=mraFwKATOEA&t=7035s)
- V2 changed nearly every heavily-loaded heat insert from "push" type to "pull-through" type versus V1.5, to reduce insert failure under load. [18:02](https://www.youtube.com/watch?v=mraFwKATOEA&t=1082s)
- Design philosophy: Milo deliberately avoids "build-to-Voron-spec" complexity — nobody actually builds the stock Voron idler-pulley nozzle probe anymore, everyone uses Klicky/Tap/Beacon/BTT Eddy PCB probes instead — so Jake wants Milo to reach a genuinely finishable, reusable state rather than an endless upgrade platform. [22:50](https://www.youtube.com/watch?v=mraFwKATOEA&t=1370s)[25:23](https://www.youtube.com/watch?v=mraFwKATOEA&t=1523s)
- LDO-supplied Y/Z motors are LDO57STH86-3004A NEMA23 steppers (3A, ~24 kg·cm / 345 oz-in) — nearly double Jake's ~175 oz-in minimum spec, leaving headroom for higher feed rates; X axis intentionally uses a smaller, cheaper motor since it carries less mass. [2:00:27](https://www.youtube.com/watch?v=mraFwKATOEA&t=7227s)[15:00](https://www.youtube.com/watch?v=mraFwKATOEA&t=900s)
- Internal "floating" bearing blocks are optional but recommended for fast builds: they don't add radial accuracy (that's the axis bearing block's job) but suppress screw whip, with ball screws more prone to whip than lead screws since they must spin faster for the same feed rate. [55:02](https://www.youtube.com/watch?v=mraFwKATOEA&t=3302s)[59:09](https://www.youtube.com/watch?v=mraFwKATOEA&t=3549s)
- Anti-backlash nut design is self-adjusting: two brass nuts are drawn together against the lead screw under spring pressure until backlash disappears, so it re-tensions itself as the screw wears — fiddlier to set up once, but maintenance-free after. [1:36:04](https://www.youtube.com/watch?v=mraFwKATOEA&t=5764s)[1:37:51](https://www.youtube.com/watch?v=mraFwKATOEA&t=5871s)
- Roadmap: V2.0 went through five internal release candidates; BOM, print list and STLs are done, but public GitHub release is blocked on finishing the written manual. [1:33:42](https://www.youtube.com/watch?v=mraFwKATOEA&t=5622s)[1:35:07](https://www.youtube.com/watch?v=mraFwKATOEA&t=5707s)
- A designer nicknamed "nine" is building a CAN-bus toolhead board and a simplified control pendant (e-stop, jog buttons, axis select, probing/macros) for the project's own motion-control firmware, "Moss"; a more full-featured pendant is being built separately by "Lotos." [31:24](https://www.youtube.com/watch?v=mraFwKATOEA&t=1884s)
- Funding: V2 development itself is fully funded via Patreon/PayPal; new donations now go toward the "Atlas" project, occasionally toward the hosts' personal costs (rent, bills). [31:24](https://www.youtube.com/watch?v=mraFwKATOEA&t=1884s)
- A co-host's own V1.5 mill had developed backlash, traced not to coolant (which the hosts say has been chemically degrading some users' 3D-printed parts elsewhere) but to two loose screws on a ball-screw locking collar. [20:42](https://www.youtube.com/watch?v=mraFwKATOEA&t=1242s)[21:11](https://www.youtube.com/watch?v=mraFwKATOEA&t=1271s)

## Details worth keeping
- LDO motor model: LDO57STH86-3004A, IP65, 3A, ~24 kg·cm (345 oz-in) — well above the 175 oz-in minimum spec. [2:00:27](https://www.youtube.com/watch?v=mraFwKATOEA&t=7227s)
- Washer issue: each anti-backlash block needs 3 conical/Belleville washers (kit ships 9 total); LDO's kit instead includes wave washers, which don't function the same way. [1:48:34](https://www.youtube.com/watch?v=mraFwKATOEA&t=6514s)
- Machining tip: precision-ground ("Blanchard ground") aluminum plate needs no facing if its thickness matches the part; otherwise buy oversized stock (e.g. 12mm for a 10mm part) and face both sides. [11:49](https://www.youtube.com/watch?v=mraFwKATOEA&t=709s)
- Lubrication tip: generic lithium grease (EP2 in the US) is fine for hobby-level lead screws; proper CNC machines run oil, but grease suits low-maintenance builds like this. [40:16](https://www.youtube.com/watch?v=mraFwKATOEA&t=2416s)
- Related in-progress projects mentioned: "Micron" (a 3D printer using Bambu A1 Mini–style PEI heated beds) and "Atlas" (the next CNC machine, currently being funded). [20:01](https://www.youtube.com/watch?v=mraFwKATOEA&t=1201s)[31:24](https://www.youtube.com/watch?v=mraFwKATOEA&t=1884s)
- A "CNC Kitchen"-designed variant of the A-side bearing block was printed and used live in place of the standard part. [50:04](https://www.youtube.com/watch?v=mraFwKATOEA&t=3004s)

## Skip it if
You aren't currently building this specific Milo/Miley V2.0 kit — the majority of the runtime is unstructured Discord banter, and the useful build/spec details are scattered in a way that only makes sense with your own kit parts in hand.
