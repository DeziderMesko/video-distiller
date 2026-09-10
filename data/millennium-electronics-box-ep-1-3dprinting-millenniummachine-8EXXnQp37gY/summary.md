# Summary: Millennium Electronics Box : Ep 1 #3dprinting #millenniummachines #opensource #filament #cncmachine

Source: https://www.youtube.com/watch?v=8EXXnQp37gY

---

I don't have web search access approved in this session, so I can't verify the less-common names (e.g. "HartK," "Nine Mile," "Bright," "West3D's Alan") against outside sources. Based on context alone, none of the proper nouns in the text show a clear, resolvable mis-hearing — the technical terms and brand/board names (Scylla, Casa, Atlas, Huanyang, BigTreeTech Kraken, Manta M8P, Octopus, Leviathan, Duet/RepRapFirmware, Klipper, Voron) all match their standard real-world spellings, and the ambiguous personal handles are exactly the kind of name the instructions say to leave alone absent stronger evidence.

Returning the text unchanged:

## TL;DR
This is a \~2-hour live build/chat stream from the Millennium Machines project (makers of the Milo desktop CNC mill), spent mostly assembling a new standalone electronics box that will work across Milo V1.5/V1.6/V2, the Casa enclosure, and even third-party routers. Between DIN-rail mounting and wiring, the streamer gives status updates on Milo V2 (release-candidate CAD, near-final BOM) and V1.6 (low priority, several months out), explains tramming technique, and talks through a side project building a "Micron" CNC sponsored by Voron-team member HartK. A large chunk is unstructured chat/banter (his dog Brisket, Monty Python, drinking jokes, YouTube monetization), so the technical payload is moderate relative to the runtime.

## Key points
- The electronics box being built is a standalone, machine-agnostic kit (works with Milo V1.5/V1.6/V2, Atlas, or any router) and will be sold separately from the mill going forward rather than bundled [8:40](https://www.youtube.com/watch?v=8EXXnQp37gY&t=520s), [15:22](https://www.youtube.com/watch?v=8EXXnQp37gY&t=922s).
- It's built around the "Scylla" control board plus a VFD, two AC power rails (24V always-on, 48V switched) and a DC cluster, with a contactor-driven e-stop safety loop so the whole AC side (motors + VFD) cuts on emergency stop [1:32:52](https://www.youtube.com/watch?v=8EXXnQp37gY&t=5572s)-[1:34:10](https://www.youtube.com/watch?v=8EXXnQp37gY&t=5650s).
- Milo V2 CAD is at release candidate 3 (likely final) with the BOM done; full CAD/BOM release expected in roughly 1-2 months [18:06](https://www.youtube.com/watch?v=8EXXnQp37gY&t=1086s), [1:57:26](https://www.youtube.com/watch?v=8EXXnQp37gY&t=7046s).
- Milo V1.6 is not a priority — it just ports V2 parts onto V1.5's existing motion system (still lead-screw driven), needs only a fitment check, and won't get an LDO kit; expect a self-sourced BOM release in about 4-5 months [22:02](https://www.youtube.com/watch?v=8EXXnQp37gY&t=1322s), [1:57:53](https://www.youtube.com/watch?v=8EXXnQp37gY&t=7073s).
- Repeated explanation for skipping ball screws: even testing with V2's more powerful motors at 55V, ball screws didn't outperform lead screws enough to justify them [23:14](https://www.youtube.com/watch?v=8EXXnQp37gY&t=1394s).
- Tramming method demoed: do a quick "dirty tram" with 1-2-3 blocks against the spindle mount first, then fine-tune with a dial indicator; V2's design decouples the FMJ from the Y-axis, making shimming/tilt adjustment easier than on V1.5/V1.6 [25:03](https://www.youtube.com/watch?v=8EXXnQp37gY&t=1503s)-[29:22](https://www.youtube.com/watch?v=8EXXnQp37gY&t=1762s).
- HartK (a Voron-team member who designed the Micron CNC and the tool-setter board originally built for Voron) is sponsoring a Micron build that will happen on-stream, with several parts to be CNC-machined instead of printed [32:24](https://www.youtube.com/watch?v=8EXXnQp37gY&t=1944s), [1:39:04](https://www.youtube.com/watch?v=8EXXnQp37gY&t=5944s).
- West3D's Alan is developing an adapter/pass-through PCB that reuses the original Milo V1.5 wiring harness and routes it into Casa's electronics bay, so builders can disconnect at the back instead of pulling the whole side panel for maintenance [1:00:02](https://www.youtube.com/watch?v=8EXXnQp37gY&t=3602s)-[1:01:11](https://www.youtube.com/watch?v=8EXXnQp37gY&t=3671s).
- New accessories now being driven by other team members rather than the streamer alone: a 4-slot stationary tool changer ("Four Pack"), a rotating turret changer ("Spice Rack", led by Bright), a fourth axis, and a pendant; "Nine Mile" is handling V2's MOS/motion files [19:53](https://www.youtube.com/watch?v=8EXXnQp37gY&t=1193s), [1:57:53](https://www.youtube.com/watch?v=8EXXnQp37gY&t=7073s).
- Firmware preference stated: Duet/RepRapFirmware's all-G-code command set (via the Duet dictionary) is preferred over Klipper's mixed Python/G-code approach, though he still runs Klipper on his own Voron printers [1:22:00](https://www.youtube.com/watch?v=8EXXnQp37gY&t=4920s)-[1:26:03](https://www.youtube.com/watch?v=8EXXnQp37gY&t=5163s).
- The channel is roughly a third of the way to YouTube's 3,000-watch-hour monetization threshold after about a third of the year, putting it on track to monetize by year-end [58:27](https://www.youtube.com/watch?v=8EXXnQp37gY&t=3507s).

## Details worth keeping
- Milo's inline MCB is rated 10A; a 20A switch is needed on the back if running a 2.2kW spindle on 110V [10:56](https://www.youtube.com/watch?v=8EXXnQp37gY&t=656s)-[1:36:37](https://www.youtube.com/watch?v=8EXXnQp37gY&t=5797s).
- A Huanyang 2.2kW VFD fits in the electronics box only with its front panel/knob removed; US builders with non-DIN-mountable 110V VFDs are asked to send an STL of their DIN mount so it can be added to the design [1:09:31](https://www.youtube.com/watch?v=8EXXnQp37gY&t=4171s)-[1:07:03](https://www.youtube.com/watch?v=8EXXnQp37gY&t=4023s).
- Comparable board tiers cited: Scylla ≈ BigTreeTech Kraken (same drivers/CAN), pricier than a Manta M8P; Octopus and Leviathan (LDO) are called out as "mainstream" boards, Manta M8P is not [1:29:54](https://www.youtube.com/watch?v=8EXXnQp37gY&t=5394s)-[1:32:00](https://www.youtube.com/watch?v=8EXXnQp37gY&t=5520s).
- Aside on machining: 7075 aluminum cuts about as well as 6061 on a rigid machine (arguably cleaner), while very soft materials (copper, MDF, softwood) are actually harder to finish well than harder ones [50:01](https://www.youtube.com/watch?v=8EXXnQp37gY&t=3001s)-[52:14](https://www.youtube.com/watch?v=8EXXnQp37gY&t=3134s).
- Support links (PayPal/Patreon) are in the stream description; funds go back into machine development [1:41:24](https://www.youtube.com/watch?v=8EXXnQp37gY&t=6084s).

## Skip it if
You're not already following the Millennium Machines/Milo CNC project — there's no general CNC tutorial content here, and most of the runtime is casual live-build narration and chat banter rather than dense technical instruction.
