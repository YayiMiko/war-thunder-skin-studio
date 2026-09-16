# Resource acquisition

Use the library first. For a new vehicle identify exact resource names in the local installation. assets/su30mkk-extraction.json is a known recipe, not a universal discovery algorithm.

extract invokes an explicitly configured external Dagor Asset Explorer source checkout. It reads game files and writes a new output directory; external code/DLLs are not bundled. Original runtime used PyQt5, zstandard, Pillow, pyperclip and requests. No auto-install. Missing pylzma is tolerated only while decoding does not require LZMA; actual use fails clearly.

Recipe: descriptor, pack, model, lod, same-pack dependencies, texture_packs (path and exact names). Paths remain inside game_root. Preserve extraction record and parser hash. After game/parser updates inspect errors and resource layout before assuming compatibility.

After extraction inspect geometry, LOD, UVs, exact materials, orientation and source colors. An all-black generated template is not usable original albedo. Keep RGBA normal alpha. Cull effects/null geometry intentionally.

Previously consulted sources (recheck for new game/shader revisions):
- https://old-wiki.warthunder.com/index.php?printable=yes&title=Custom_skins
- https://wiki.warthunder.com/cdk/232-3d-models-for-aircraft
- https://wiki.warthunder.ru/cdk/creation_camo

Legacy documentation and shaders differ. R/B material and G/A normal packing is a case-specific starting point. Damage substitution is not inferred.
