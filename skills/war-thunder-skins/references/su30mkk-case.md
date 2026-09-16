# Su-30MKK / Shorekeeper

Evidence date 2026-09-17. The commissioning user confirmed V3 in game with a screenshot retained in their private archive. This validates that package, not every future generic output. Damage and other vehicles remain unverified. Private archives and screenshots are not included in this repository.

Known profile: su_30mkk LOD0, su_30mkk_skeleton; main material su_30mkk_aircraft_normal_detail_lo. Source maps 2048². Targets su_30mkk_c* / su_30mkk_n*. OBJ import NEGATIVE_Z/Y yields x=nose, y=port, z=up. Exclude dynamic_null, gunfire, jet_flame, propmask effects.

Material: R inverse roughness, B metallic; retain G/A exactly. Blender Non-Color + CHANNEL_PACKED avoids alpha corrupting channel interpretation; reconstruct positive normal Z. Flip bottom-up Blender pixels for top-down Pillow packing. The game-generated template was all-black; real source extraction was necessary.

First design failed visually: character too small, empty cyan areas, mismatched matte finish, misplaced lettering and uncertain normals. The idea of an aircraft becoming the character, engines as legs below the dress, was positively received. Preserve it as an option, not a mandatory template.

V3 increased dorsal character size and gloss. User still wanted stronger element design, leading to early concept visualization. Later A CELESTIAL GOWN and B BUTTERFLY TIDE were workflow-test concepts, not chosen production replacements. Do not claim V3 implements either.

External library: vehicles/su_30mkk holds reusable technical data; orders/shorekeeper-su30mkk-v3/archive preserves historical scripts, scene and evidence. Historical scripts have hardcoded machine paths and are not the generic CLI. case.json records provenance/status. New orders get new IDs and their own recipes.
