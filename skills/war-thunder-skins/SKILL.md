---
name: war-thunder-skins
description: Design War Thunder vehicle skins and character itasha, from early whole-aircraft concept paintovers to real-model projection, packed normals, UV baking, packaging and reusable vehicle archives. Includes the user-confirmed Su-30MKK Shorekeeper case.
---

# War Thunder Skins

## Start cheaply

Honor planning-only or concept-only scope. Resolve this plugin root (two parents above this skill directory). Run `python <plugin>/scripts/studio.py doctor` and `list` once when environment/vehicle discovery is needed; reuse their results until something changes. Environment: `~/.config/war-thunder-skin-studio/environment.json`; large assets live in its external library. Read only the selected vehicle/order and relevant reference, not old conversation dumps or entire logs.

Reuse registered models, original textures and neutral views. For a new vehicle, read [extraction.md](references/extraction.md). Create orders with `new-order --vehicle ID --id ID --art PATH --theme TEXT`. Inspect original artwork once when composition requires it; check alpha/dimensions by script and reuse established source facts.

## Concept before production

Early previews are overall visual designs made from the aircraft model and main artwork, not production previews or parameter sliders.

- Reuse neutral top/oblique views; `baseline` generates them if absent. Use the available ImageGen workflow and read its skill when invoked. Supply actual model views and original art. No silent API/tool substitution.
- Usually make two materially different compositions, one image per direction, moderate resolution and comparable camera. Spend effort on focal hierarchy, dominant shapes, negative space, typography zones and finish.
- For this user's itasha, the character must dominate at thumbnail size. A tiny sticker amid empty wings fails unless explicitly requested. Scale alone does not fix composition; protect face/hands from seams and severe stretching.
- Preserve aircraft and character identity. Label paintovers as concepts: geometry, lettering and cross-view consistency remain approximate until projected onto the real mesh.
- Record an actual choice with `choose`. Never fabricate user selection. Explicit autonomous design authorization permits `agent-authorized` with the actual reason; prior authorization remains valid.
- Stop at concepts when requested. See [workflow.md](references/workflow.md) for acceptance and cost controls.

## Production

1. Read [schema.md](references/schema.md). Translate the selected concept into order layers, model-space coordinates and finish. A concept PNG alone is not a reproducible recipe.
2. Preserve sources and use new version directories. Select exact material names, not numeric indices. Before placing decals, derive target bounds, axes, mirrored-side behavior and clipping constraints from the actual mesh/UVs. Typeset exact text assets. Check placement numerically where supported; do not guess coordinates and compensate with repeated full bakes.
3. Batch the requested changes, then use one low-cost `preview` when needed. Generate views for the user; rendering images does not require sending them to the model. Once the requested implementation and objective checks are ready, run one `bake --size 4096` into a fresh output directory. Use 8K only when requested or demonstrably needed.
4. Run `validate` and targeted checks for changed behavior. Current packer preserves original G/A bytes and writes R/B for the verified aircraft material. Other packing requires a dedicated adapter. Packed images must retain alpha and use Non-Color plus CHANNEL_PACKED in Blender. Exported-texture renders are human review artifacts by default.
5. `install PACKAGE --skin-name NEW_ID` writes a new UserSkins folder and refuses overwrite. This fits authorized production delivery; respect narrower user scope. Human visual review need not block authorized delivery; label it pending. Never alter game archives or runtime executables.
6. Report objective validation, AI visual inspection (if any), human visual acceptance and game verification separately. Neither a successful bake nor a generated preview proves visual acceptance or game correctness.

## Token economy and acceptance

Default: AI implements and performs objective checks; the user owns subjective visual acceptance. Do not routinely ask who should review. Complete authorized development without waiting for optional aesthetic approval.

- Do not load every generated view with image tools. Link saved previews or a contact sheet for the user. One initial source/concept inspection is allowed when necessary for implementation; do not re-read unchanged images.
- Use AI visual inspection only for an explicit request or a concrete defect that needs visual evidence. Default to one focused pass of at most two cropped/downscaled images per revision batch, then fix the named issue and run objective checks. Do not use a contact sheet to smuggle in an exhaustive multi-view audit. Broader explicit user scope overrides this default.
- Resolve known objective failures before delivery. Stop aesthetic iteration after the requested changes and checks; do not invent new embellishments, re-layouts, cameras or repeated final bakes. If visual ambiguity remains, deliver it as pending human review instead of silently looping.
- Prefer existing numeric checks for bounds, overlap, projection coverage, text orientation and UV seams. Add a reusable check only when justified by the actual defect; do not build a general validator for every task. Report unsupported checks honestly.
- Batch independent reads and related edits. Read changed sections, concise summaries and error log tails; keep full logs/artifacts on disk. Do not replay prior conversations or repeatedly read skills/references already loaded.
- Wait for render/build completion using the tool's normal wait (typically 30-60 seconds), not repeated one-second polling. Combine status retrieval with useful work; a poll needs no separate image review.
- Keep a short order-local checkpoint at phase boundaries: selected design, modified files, objective results, outstanding defects, preview/package paths and next action. Update that file instead of appending long narrative copies. On resume, read it before history. Do not create/fork threads automatically.
- If the user requests stop or warns that quota is nearly exhausted, stop starting iterations immediately. Preserve the current state, summarize incomplete work and return; do not turn stopping into another visual acceptance or bake cycle.

These are workflow defaults, not hard token metering. Do not claim measured savings without comparable usage evidence.

## Offline review by default

Use cached neutral views, low-cost real-mesh renders and exported-texture renders for routine preview and delivery. Do not launch or navigate War Thunder, load computer-use tools for game review, or run camera/screenshot loops. In-game verification is optional and requires an explicit request for the current order; do not routinely ask for it. If the user cancels it, stop immediately and continue offline.

Record unperformed game verification honestly as not performed; it does not block an otherwise validated offline delivery. User-provided game screenshots may supply separate evidence without launching the game. After saving outputs, close tools launched for this task; honor explicit requests to close existing game/3D tools while protecting unsaved work.

## Transfer knowledge

Read [su30mkk-case.md](references/su30mkk-case.md) for this vehicle or related failures. It records the first confirmed case, not a universal composition. Keep models, art, editable scenes, selected concepts, package and evidence in the external library with source hashes. Historical scripts have hardcoded paths and are archived as history, not generic tools.

Capture new vehicle exceptions in profiles and regression cases; keep this entry concise. Reuse technical evidence rather than copying the first aircraft's design. CLI scripts need no MCP service. Add MCP only if a real persistent/interactive integration becomes necessary. Do not update assistant memory as a side effect.
