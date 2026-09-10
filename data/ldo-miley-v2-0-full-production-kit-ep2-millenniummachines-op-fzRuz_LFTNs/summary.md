# Summary: LDO Miley V2.0 (full production kit) Ep2 #millenniummachines #opensource #cnc

Source: https://www.youtube.com/watch?v=fzRuz_LFTNs

---

## TL;DR
This is an unedited \~2.5-hour livestream from the Milo CNC-mill project (Millennium Machines design, LDO-produced kit). The host, a member of the dev team, picks up the V1.x kit build where last stream's Z-axis left off and works through the Y-axis (bearing block, heat-set inserts, an optional frame-stiffening mod, and one anti-backlash lead-screw nut). Actual assembly is a minority of the runtime — most of the stream is live chat: filament-price griping, a rundown of Milo's automatic-tool-changer options, warnings against cheap collets, a 3D-print quoting spreadsheet, and off-topic banter (dogs, anime, a theft story). Useful mainly if you're building this specific kit or shopping for its ATC add-ons.

## Key points
- Resumes the Milo build on the Y-axis: bearing block assembly with heat-set inserts run at 310→340°C for the glass/carbon-filled polycarbonate parts (well above their 280°C print temp) [5:46](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=346s), [8:46](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=526s).
- Optional "blind joint" frame mod: bolts the Y-plate straight into the column (M5x30) instead of relying only on the 90° corner brackets — small stiffness gain, but makes tramming more annoying since you have to lift and shim the whole plate [15:22](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=922s), [1:22:56](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=4976s).
- Milo's two ATC options compared: the "four-pack" (4 fixed tool bays, simplest/cheapest) vs. "Spice Rack" (6–8 tools on a rotary axis, more flexible, more expensive and complex); fixturing alone (collets + nuts) runs close to $80 before any actual tooling [42:33](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=2553s), [45:32](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=2732s).
- The tool-changer's clamping torque is unproven for ER16 collets: only an ER20 prototype (built by teammate Bright) has been torque-tested so far, and ER16 has less mechanical leverage, so those results may not carry over [39:08](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=2348s), [40:18](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=2418s).
- Firm rule from the host: never buy cheap collets or collet nuts (e.g. Amazon 5-for-£20 packs) — measured 0.5mm of runout from bad ones; cut costs on end mills instead if you must [48:03](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=2883s).
- UK glass-fiber ABS pricing has nearly doubled — a 10kg bag from Bambu Lab is now about £248 — and each Milo axis alone eats roughly 3kg of filament [20:02](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=1202s), [21:48](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=1308s).
- Rough estimate for the full Milo kit price: about £2,000 all-in (\~$1,600 for the mill, \~$400 for the electronics bay), though not finalized [41:13](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=2473s).
- On pricing print jobs for others: the host's quoting spreadsheet (adapted from CNC Kitchen's Stefan) shows labor, not material or machine time, is the single biggest cost in any print job [41:47](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=2507s), [42:03](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=2523s).
- Host declines to run an official community "milling activity"/part-fulfillment program for Milo owners, citing quality-control overhead and the fact that JLC is cheaper and tighter-tolerance anyway [1:36:52](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=5812s), [1:38:56](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=5936s).
- Anti-backlash lead-screw nut assembly demoed live as a recurring teaching segment: brass TR8 nut, dowel pins, Belleville washers stacked peak-to-peak, preloaded with M3x40 bolts tightened a quarter-turn at a time in a star pattern [1:53:22](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=6802s), [1:57:48](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=7068s).

## Details worth keeping
- Fastener conventions for this kit: M5x8 into T-nuts from the side, M5x10 for most T-nut fastenings, M5x12 for blind joints into extrusion ends, M3x8 for 90° corner connectors [30:22](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=1822s).
- Glass-fiber vs. carbon-fiber filled parts: glass-fill is stiffer but weaker on impact, heavier, and damps vibration noticeably better than carbon-fill — carbon-fill's main edge is being lighter, which matters more for 3D-printed parts than for milled ones [1:30:08](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=5408s).
- For soft jaws/V-blocks: use the vendor's downloadable reference CAD template rather than modeling from scratch [2:07:25](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=7645s).
- Safety point hammered on repeatedly: don't clamp oversized stock in an undersized vise or on the 4th-axis fixture — that's how you break the part or the machine [2:09:17](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=7757s), [2:10:15](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=7815s).
- "Atlas," the host's larger CNC machine currently in CAD, likely won't ever ship as a kit — it's too big to be practical to ship [23:03](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=1383s), [1:00:46](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=3646s).
- Two theft anecdotes shared in chat: a viewer's Voron parts (\~1.6 plates worth) were stolen, and another had an ASA filament order stolen within two hours of delivery, with the empty package later found nearby [1:06:49](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=4009s), [1:10:02](https://www.youtube.com/watch?v=fzRuz_LFTNs&t=4202s).

## Skip it if
You're not building this specific LDO/Millennium Machines Milo kit or shopping for its tool-changer options — this is a raw livestream where hands-on build content is a small fraction of the runtime, padded with filament-price complaints, anime/dog chat, and the host correcting a viewer's vise technique.
