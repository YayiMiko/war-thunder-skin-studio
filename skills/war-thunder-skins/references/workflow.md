# Design stages and economy

1. Concept: actual neutral aircraft views + main artwork -> two overall directions. Solve focal hierarchy, color masses, character scale, silhouette, balance and text zones. Use comparable cameras. No bake or game launch.
2. Real mesh draft: selected design -> projected low-cost render. Resolve seams, stretching, mirrored UVs, typography and material response before detailed production.
3. Production: high-resolution maps, exact BLK, packed normals, exported-map renders, new installed skin, then game evidence.

Label images by stage. Never present an AI paintover as installed texture evidence.

Review at thumbnail size: character/theme should read before stripes/emblems. Avoid arbitrary pale expanses and competing ornaments. Face/hands should survive geometry cuts. Supporting shapes should follow aircraft and artwork flow. Text needs independently checked port/starboard orientation. Match finish to illustration with selective gloss; preserve readable panel normals. Packed-normal alpha is data, not transparency.

Reuse model and baseline cache. Carry decisions in one order file. Read only stage-relevant references. Inspect log tails when failures arise; avoid repeated long outputs and screenshots. Two concepts, advance one, then targeted revisions. Do not re-extract on every change. Image generation has separate variable cost, not eliminated by this plugin. No automated game UI loop is included.
