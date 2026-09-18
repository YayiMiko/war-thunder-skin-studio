# Design stages and economy

Follow the token economy and acceptance defaults in SKILL.md. AI handles implementation and objective correctness; the user handles visual acceptance unless they explicitly delegate it.

1. Concept: actual neutral aircraft views + main artwork -> usually two directions. Solve hierarchy, color masses, character scale and text zones. Supply concepts to the user; no production bake or game launch.
2. Real mesh draft: first record the reference-layout table required by SKILL.md; calibrate color boundaries and main graphic proportions against a corresponding camera. Derive placement from mesh/UV bounds and target axes before rendering. Batch changes and generate one low-cost preview set. Use numeric coverage/orientation checks where available, separately from reference fidelity. Do not shrink graphics to improve coverage or substitute repeated visual guessing.
3. Production: bake once after requested changes and objective checks, validate maps/BLK/normal channels, and deliver the new package plus exported-map previews. A specific failure justifies a targeted fix and rerun; optional aesthetic concerns do not justify endless iteration.

Label images by stage. AI paintovers are concepts; generated render files are review artifacts, not evidence that anyone inspected or accepted them.

Human review checklist: thumbnail hierarchy; face/hands and major logos clear of cuts; text readable on both sides; seams/stretching; wings/tails/belly; finish and panel details. Supply this checklist with relevant preview links when useful. Do not automatically feed every view back to the model.

For a named visual defect, inspect only the relevant crop(s), default at most two images in one pass per revision batch. Reuse unchanged observations. Explicit exhaustive AI review may exceed that default; keep it scoped to the requested regions and stop when criteria are met.

Reuse vehicle/baseline caches and carry decisions in the order plus a short checkpoint. Keep raw logs and high-resolution views on disk. Use normal completion waits rather than rapid polling. Geometry validation uses available measured data; do not label unimplemented checks as passed.

Do not launch/control the game for previews or screenshots unless explicitly requested for this order. Canceled game review stops immediately. Missing human/game acceptance does not block an otherwise authorized offline delivery; mark both pending/not performed as appropriate.

Image generation has separate variable cost. Local rendering time, image file bytes, model tokens, cached inputs and subscription quota are different measures; do not conflate them or promise a fixed saving.
