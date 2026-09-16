---
name: war-thunder-skins
description: Design War Thunder vehicle skins and character itasha, from early whole-aircraft concept paintovers to real-model projection, packed normals, UV baking, packaging and reusable vehicle archives. Includes the user-confirmed Su-30MKK Shorekeeper case.
---

# War Thunder Skins

## Start cheaply

Honor planning-only or concept-only scope. Resolve this plugin root (two parents above this skill directory). Run `python <plugin>/scripts/studio.py doctor` and `list`. Environment: `~/.config/war-thunder-skin-studio/environment.json`; large assets live in its external library. Read only the selected vehicle/order and relevant reference, not old conversation dumps or entire logs.

Reuse registered models, original textures and neutral views. For a new vehicle, read [extraction.md](references/extraction.md). Create orders with `new-order --vehicle ID --id ID --art PATH --theme TEXT`. Inspect original artwork and alpha.

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
2. Preserve sources and use new version directories. Select exact material names, not numeric indices. Run `preview` for real geometry review. Check both sides, text orientation, seams, wings, tails and belly. Typeset exact text assets instead of trusting generated lettering.
3. Once composition is settled, run `bake --size 4096` into a fresh output directory. Lower resolutions suit verification; use 8K only when source quality and visible detail justify it.
4. Run `validate` and inspect exported-texture renders. Current packer preserves original G/A bytes and writes R/B for the verified aircraft material. Other packing requires a dedicated adapter. Packed images must retain alpha and use Non-Color plus CHANNEL_PACKED in Blender.
5. `install PACKAGE --skin-name NEW_ID` writes a new UserSkins folder and refuses overwrite. This fits authorized production delivery; respect narrower user scope. Never alter game archives or runtime executables.
6. Record file validation, Blender visual review and in-game/user verification separately. A successful bake is not game verification. Damage replacements need separate evidence.

## Transfer knowledge

Read [su30mkk-case.md](references/su30mkk-case.md) for this vehicle or related failures. It records the first confirmed case, not a universal composition. Keep models, art, editable scenes, selected concepts, package and evidence in the external library with source hashes. Historical scripts have hardcoded paths and are archived as history, not generic tools.

Capture new vehicle exceptions in profiles and regression cases; keep this entry concise. Reuse technical evidence rather than copying the first aircraft's design. CLI scripts need no MCP service. Add MCP only if a real persistent/interactive integration becomes necessary. Do not update assistant memory as a side effect.
