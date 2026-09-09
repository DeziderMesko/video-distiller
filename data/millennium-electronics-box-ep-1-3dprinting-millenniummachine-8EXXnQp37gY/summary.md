# Summary: Millennium Electronics Box : Ep 1 #3dprinting #millenniummachines #opensource #filament #cncmachine

Source: https://www.youtube.com/watch?v=8EXXnQp37gY

---

## TL;DR
This is a long, casual livestream from Millennium Machine Works building an "electronics box" for their Milo CNC line — a standalone, machine-agnostic enclosure housing the Sila control board, VFD, power supplies, contactor, and e-stop circuitry. Roughly the first half-hour covers actual build work (mounting DIN rails and components); the rest is Q&A and chit-chat about the V2/V1.6 roadmap, Atlas, a Micron build sponsorship, firmware opinions (RepRapFirmware/Duet vs. Klipper), and community/partner news. There's minimal step-by-step instructional value — it's more a progress update plus open Q&A than a tutorial.

## Key points
- The electronics box is being designed as a standalone, portable enclosure that can attach to any machine (V2, V1.6, Miley, Milo, or even a third-party router) rather than being bundled into a specific mill kit as before.
- Box interior fits: two AC power clusters, one DC cluster, 24V and 48V power supplies, a contactor, MCB (10A shown, up to 20A for 2.2kW spindles on 110V), Sila board, and a VFD (Huanyang 2.2kW only fits with its front panel removed); box dimensions are 410×400mm, deliberately smaller than a team member's requested 500×500.
- Safety architecture explained in detail: 24V supply stays always-on to power VMOS/VMCU; AC cluster 1 → 24V supply → contactor → AC cluster 2 → 48V motor supply and VFD; e-stop trips a relay that opens the contactor, cutting AC to motors and VFD (a proper industrial-style safety loop, not just a switch).
- V2 CAD is at release candidate 3 (likely final); bomb (bill of materials) and CAD release for V2 expected within 1-2 months, followed by V2 manuals.
- V1.6 is explicitly not a priority — release (CAD + BOM) expected roughly 4-5 months out, after V2 and the electronics box; V1.6 motion system is essentially unchanged from V1.5 (just thrust bearings added), so extensive re-testing isn't needed.
- Electronics kits will now be sold separately from the mill kits, sourceable independently for any supported machine.
- A community-designed adapter/pass-through board (by "Alan" at West3D) lets Casa builders reuse original V1.5 LDO wiring and unplug the whole harness from the back rather than disassembling the electronics bay for maintenance.
- Team is building a Fabrico Micron CNC on stream, sponsored by Hartk (the Micron's designer, now an honorary Millennium team member and designer of the tool-setter board used across their machines).
- Atlas (a larger CNC) remains on the back burner with no development progress — compared to Voron's long-vaporware "Phoenix" project.
- Two new tool-changer accessories are teased: a 4-tool stationary changer ("Four Pack") and a rotating turret changer ("Spice Rack"), plus ongoing fourth-axis and pendant development by other team members.
- Firmware take: presenter prefers RepRapFirmware/Duet over Klipper, citing better unified documentation (single G-code dictionary vs. Klipper's Python+G-code split) and not needing a separate SBC/Raspberry Pi.
- Channel is about one-third of the way to YouTube's 3,000 watch-hour monetization threshold, on pace to hit it by year-end.

## Details worth keeping
- MCB used: 10A (size must match spindle/region — don't just grab any breaker).
- Box interior: 410mm × 400mm.
- US builders with non-DIN-mountable 110V VFDs asked to send the presenter STLs/reference so a mount can be designed.
- Recommendation against ball screws (referenced as previously covered in another video) — lead screws preferred partly because their friction prevents axis drop on power loss, which ball screws don't provide as well.
- Tramming tip: do a "dirty tram" first using 1-2-3 blocks against the spindle before fine-tuning with an indicator.
- Cutting note: 7075 aluminum cuts about as easily as 6061 on a rigid machine like Milo, with a possibly better finish; copper is called out as unusually hard to machine.
- Links mentioned in chat/description: Thomas's Voron-inspired DIN mount STLs on Printables, West3D/Alan's pass-through adapter board, project Patreon/PayPal support links.

## Skip it if
You want a structured build tutorial or finalized specs/files — nothing here is released yet (no BOM, no STLs for this box), and the bulk of the stream is unstructured chat, banter, and repeated Q&A rather than concentrated technical instruction.
