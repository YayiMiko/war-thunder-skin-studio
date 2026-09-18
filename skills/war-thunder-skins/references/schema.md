# Schema and commands

`python <plugin>/scripts/studio.py --help` lists commands. Global `--config PATH` precedes the command. Vehicle/order paths resolve relative to their JSON. Logs stay in output directories; stdout is compact JSON.

Configure once: `configure --library PATH --game PATH --blender EXE [--dae-root PATH --dae-python EXE]`. Reconfiguration requires intentional `--replace`.

Register: `register --id ID --model OBJ --color PNG --normal RGBA_PNG --material EXACT_NAME --color-target "texture_c*" --normal-target "texture_n*" [--baseline BLEND]`. Repeat --material for slots sharing maps. Multiple paint_sets require distinct IDs, material names, maps and replacement targets. A material belongs to one set only. OBJ sibling .mtl is copied; copy other dependencies when needed. Other model formats need a neutral baseline blend.

Vehicle keys: import_axes, cull_material_patterns, camera_target, camera_scale, paint_sets, validation. Preview normal_x/normal_y/invert_y are configurable. Production packer always preserves G/A and writes R/B; different packing requires another adapter.

Order keys: ID, vehicle, art, theme, directions, concept, finish, layers, validation. `choose --order ID --image PATH --decision TEXT [--decided-by user|agent-authorized]` records a real decision. The CLI cannot establish whether a claimed user decision is truthful.

Layers apply in array order. Common keys: set (default main), type, mask, roughness/metalness (0..1). finish supplies defaults; preview_coat only affects Blender and is not a guaranteed game parameter.

- solid: color is four linear RGBA values. Use mask.opacity for blending.
- band: color, axis, offset, positive half_width; abs(dot(position,axis)+offset)<half_width.
- image: image path, origin at projected lower-left, perpendicular unit u_axis/v_axis, size [width,height] in world model units. Optional crop [u0,v0,u1,v1] uses normalized bottom-left coordinates. Alpha is respected. Preserve aspect unless intentionally deforming.
- mask: optional normal [x,y,z], min_dot default .2, bounds {x:[min,max],...}, opacity 0..1.

Example dorsal projection for the verified Su axes x=nose, y=port, z=up (not historical V3 coordinates):

```json
{"type":"image","image":"assets/character.png","origin":[-7,-4,0],"u_axis":[0,1,0],"v_axis":[1,0,0],"size":[8,13],"mask":{"normal":[0,0,1],"min_dot":0.2}}
```

Check mirrored UV constraints numerically where available; they may prevent independent sides. Generated renders are for human review by default; use the bounded AI inspection policy in SKILL.md. baseline outputs three neutral views; preview outputs three layer views; bake outputs five exported-map views, a packed scene, controls, TGA/BLK and package.json. Normal maps retain native dimensions; albedo follows --size. Construction materials Studio_<set> remain in the baked scene, while objects display Exported_<set>. Regenerate from JSON or restore construction materials to edit.

Validation checks sizes, format, uniform-color exceptions, hashes, exact BLK and preserved G/A. It does not prove UV coverage, text, engine parity or damage. Keep source-normal archive for validation; installed game skin needs images and BLK. Installation refuses existing directories.
