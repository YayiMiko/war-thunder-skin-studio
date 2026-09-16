"""Read-only adapter around an explicitly configured, existing DAE checkout."""
import importlib.util,json,sys,types,hashlib
from pathlib import Path

def main():
    job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));env=job['environment'];r=job['recipe'];out=Path(job['out']);game=Path(env['game_root'])
    src=Path(env['dae_root'])/'src/dae';sys.path.insert(0,str(src))
    if not importlib.util.find_spec('pylzma'):
        # Zlib/Zstd sample was verified. Do not substitute an incompatible LZMA dialect.
        missing=types.ModuleType('pylzma')
        def unavailable(*a,**kw):raise RuntimeError('This resource needs the optional pylzma codec; install a compatible codec or choose a supported exporter.')
        missing.compress=missing.decompress=unavailable;sys.modules['pylzma']=missing
    from parse.gameres import GameResourcePack,GameResDesc
    from parse.material import DDSxTexturePack2
    from util.assetcacher import AssetCacher
    from PIL import Image
    records=[]
    def source(rel):
        p=(game/rel).resolve()
        if game.resolve() not in p.parents:raise ValueError('Resource recipe must stay inside game_root')
        return p
    desc=GameResDesc(str(source(r['descriptor'])));desc.loadDataBlock();AssetCacher.appendGameResDesc(desc)
    pkg=GameResourcePack(str(source(r['pack'])))
    for n in r.get('dependencies',[]):AssetCacher.cacheAsset(pkg.getResourceByName(n))
    model=pkg.getResourceByName(r['model']);model.getModel(int(r.get('lod',0))).exportObj(str(out),exportTexture=False)
    for pack in r.get('texture_packs',[]):
        remaining=set(pack['names']);tp=DDSxTexturePack2(str(source(pack['path'])))
        for t in tp.getPackedFiles():
            if t.name not in remaining:continue
            if Path(t.name).name!=t.name or any(ch in t.name for ch in '<>:"/\\|?*'):raise ValueError('Unsafe resource name')
            t.exportDDS(str(out));im=Image.open(out/(t.name+'.dds'));im.save(out/(t.name+'.png'))
            records.append({'name':t.name,'size':list(im.size),'mode':im.mode,'pack':pack['path']});remaining.remove(t.name)
        if remaining:raise ValueError('Missing requested textures: '+str(sorted(remaining)))
    report={'model':r['model'],'lod':r.get('lod',0),'textures':records,'adapter':'external Dagor Asset Explorer','dae_parser_sha256':hashlib.sha256((src/'parse/realres.py').read_bytes()).hexdigest(),'scope':'Extraction completed; geometry/UV visual review still required.'}
    (out/'extraction.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if __name__=='__main__':main()
