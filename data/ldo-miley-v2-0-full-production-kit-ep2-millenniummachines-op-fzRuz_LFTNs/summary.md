# Summary: LDO Miley V2.0 (full production kit) Ep2 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=fzRuz_LFTNs

---

## TL;DR
This is a ~2h23m livestream VOD from Millennium Machine Works (channel covering the open-source "Milo" CNC mill, built around LDO Motors hardware) — Episode 2 of assembling the "LDO Milo V2.0" full production kit. The host continues the build from the Z-axis (done in Ep1) into the Y-axis: bearing blocks, an optional stiffening frame mod, and an anti-backlash nut assembly, while fielding a steady stream of viewer questions about tool-changer options, collet quality, filament choice, and 3D-print pricing. It's a casual, chat-heavy stream with long off-topic tangents (weather, filament costs, anime, a viewer's stolen 3D-printer parts) rather than a tight tutorial, and the Y-axis is left unfinished (rails to be added off-camera).

## Key points
- Continues Y-axis assembly after finishing the Z-axis in Episode 1: bearing blocks, heat-set inserts, frame corner brackets, anti-backlash nut, thrust bearing/locking collar, floating bearing block.
- Bolt cheat sheet given repeatedly: M5x8 for most 90° corner connectors and T-nuts, M5x10 for occasional T-nut cases, M5x12 for blind joints, M3x8 for 90° corner connectors, M5x30 for the longer (non-structural, anti-sliding) bolts into the column side channel.
- Performs an optional frame mod: blind-jointing the front plate directly into the column extrusion instead of resting it on 90° corner blocks, for extra rigidity — trade-off is you must lift the whole plate (not just shim under the blocks) when tramming.
- Detailed comparison of automatic tool changer options: the "four-pack" (4 fixed bays, simplest/cheapest, but tooling+collets+nuts alone run ~$80+) versus "Spice Rack" (6–8 tools, rotary axis, more flexible but pricier and more complex). Both need a 5th stepper driver via the CAN-connected "Ultralight" board, only required if a 4th axis is also in use.
- Strong warning against cheap eBay/Amazon ER collet nuts — reports up to 0.5mm of runout from bad ones; recommends at least AA-rated (or better) collets even while going cheap on other tooling.
- Glass-fiber vs. carbon-fiber filled printed parts: glass fiber is stiffer, heavier, cheaper, and damps vibration better (his pick for CNC machine parts); carbon fiber is lighter (better for 3D-printer moving parts) but propagates vibration, making it a poor CNC choice.
- Walks through the anti-backlash nut build on the lead screw: TR8 brass nuts, a grub screw for the grease port, Belleville washers installed peak-to-peak, preloaded via M3x40 bolts tightened a quarter-turn at a time in a star pattern, then packed with lithium grease.
- LDO is dropping carbide tooling/collet stock due to high carbide prices and won't bundle a full four-pack ATC kit (may do a Spice Rack kit instead); DMS (UK supplier) will stock some Milo V2 kits.
- Explains his 3D-print quoting spreadsheet (adapted from Stefan/CNC Kitchen's) that factors bed-change time, slicing time, and a minimum $/hour target — emphasizes labor, not material, is the dominant cost.
- Critiques a viewer's proposed 3D-printed flood-coolant enclosure for the Milo, explaining the table's Y travel makes the back-panel geometry physically impossible without a much deeper bench.

## Details worth keeping
- Heat-insert temperature for polycarbonate parts: 310–340°C (vs. 280°C used to print them).
- Rough full Milo kit price: ~£2,000 (~£1,600 for the mill, ~£400 for electronics).
- Glass-fiber ABS filament price from Bambu Lab jumped to £248 per 10kg (nearly doubled, attributed to tariffs).
- Points viewers to LDO's own soft-jaw/V-block CAD templates on their website instead of modeling from scratch.
- Warns against clamping oversized or heavy stock in undersized vises or on the fourth axis — calls it "a recipe for disaster."

## Skip it if
You want a clean, step-by-step build tutorial — this is a rambling livestream with only partial Y-axis progress and heavy unrelated chat banter; better suited to build-log completionists or regular viewers of the channel than someone trying to follow the Milo manual efficiently.
