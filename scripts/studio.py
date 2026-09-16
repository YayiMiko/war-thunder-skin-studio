"""Local War Thunder skin workflow. Run --help; no API keys or network required."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = Path.home()/'.config'/'war-thunder-skin-studio'/'environment.json'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stamp(): return datetime.now(timezone.utc).isoformat()
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def identifier(s):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}',s): raise ValueError('Use 1-64 lowercase letters, digits, hyphens or underscores; no paths.')
    return s
def resolve(base,p):
    path=Path(p).expanduser()
    return (path if path.is_absolute() else Path(base)/path).resolve()
def inside(base,name):
    base=Path(base).resolve();p=(base/name).resolve()
    if p==base or base not in p.parents: raise ValueError(f'Path leaves destination: {name}')
    return p
def newdir(p):
    p=Path(p)
    if p.exists(): raise FileExistsError(f'Output already exists; choose a new version: {p}')
    p.mkdir(parents=True);return p.resolve()
def image_info(path):
    from PIL import Image
    with Image.open(path) as im:
        im.load();e=im.convert('RGB').getextrema()
        return {'format':im.format,'mode':im.mode,'size':list(im.size),'rgb_extrema':e,
                'flat_rgb':all(a==b for a,b in e),'all_black':all(b==0 for a,b in e),'sha256':digest(path)}
def copy(p,out):
    p=Path(p)
    if not p.is_file():raise FileNotFoundError(p)
    Path(out).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
def config(args):
    p=Path(args.config).expanduser()
    if not p.is_file():raise ValueError(f'No environment at {p}; run configure first.')
    c=read(p)
    for k in ['library','game_root','blender']: c[k]=str(resolve(p.parent,c[k]))
    return c
def vehicle(c,name):
    p=Path(c['library'])/'vehicles'/identifier(name)/'vehicle.json';return p,read(p)
def order(c,name):
    p=Path(c['library'])/'orders'/identifier(name)/'order.json';return p,read(p)
def run_logged(argv,out,timeout=600):
    with Path(out).open('w',encoding='utf-8') as f:
        result=subprocess.run([str(a) for a in argv],stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    if result.returncode: raise RuntimeError(f'Process failed ({result.returncode}); see {out}')
def blender(c,job,out):
    out=newdir(out);job['out']=str(out);job['python']=sys.executable;write(out/'job.json',job)
    run_logged([c['blender'],'-b','-t','6','--python-exit-code','1','--python',PLUGIN/'scripts'/'blender_driver.py','--',out/'job.json'],out/'blender.log')
    if not (out/'result.json').is_file():raise RuntimeError(f'Blender did not produce result.json; inspect {out}/blender.log')
    return read(out/'result.json')

def validate_package(folder):
    from PIL import Image
    import numpy as np
    p=Path(folder).resolve();manifest=read(p/'package.json');identifier(manifest['vehicle'])
    entries=manifest['textures'];seen=set();pairs=[];info=[]
    if not entries:raise ValueError('No textures in package')
    for e in entries:
        name=e['file'];identifier(Path(name).stem)
        if Path(name).name!=name or Path(name).suffix.lower() not in ['.tga','.dds']:raise ValueError('Texture filenames must be plain TGA/DDS names')
        target=e['from']
        if not re.fullmatch(r'[A-Za-z0-9_]+\*?',target) or target in seen:raise ValueError(f'Invalid or duplicate texture target: {target}')
        seen.add(target);path=inside(p,name);ii=image_info(path)
        if ii['format']!={'.tga':'TGA','.dds':'DDS'}[Path(name).suffix.lower()]:raise ValueError(f'Extension/content mismatch: {name}')
        if any(n<4 or n>8192 or n&(n-1) for n in ii['size']):raise ValueError(f'Expected power-of-two dimensions <=8192: {name}')
        if e['role']=='color' and ii['flat_rgb'] and not e.get('allow_flat',False):raise ValueError(f'Uniform color image requires intentional allow_flat: {name}')
        if e['role']=='normal':
            im=Image.open(path)
            if im.mode!='RGBA':raise ValueError(f'Packed normals require RGBA: {name}')
            ref=resolve(p,e['normal_source']);a=np.array(im);b=np.array(Image.open(ref).convert('RGBA'))
            if a.shape!=b.shape or not np.array_equal(a[:,:,[1,3]],b[:,:,[1,3]]):raise ValueError(f'Packed G/A normals changed: {name}')
        if e['role'] not in ['color','normal']:raise ValueError(f'Unsupported role: {e["role"]}')
        if e.get('sha256') and e['sha256']!=digest(path):raise ValueError(f'Hash mismatch: {name}')
        pairs.append((target,name));info.append({'file':name,**ii})
    blk_name=identifier(manifest['vehicle'])+'.blk';blk=inside(p,blk_name).read_text(encoding='utf-8-sig')
    expected=make_blk(pairs)
    if blk!=expected:raise ValueError('BLK differs from declared exact replace_tex mappings')
    return {'ok':True,'files':info,'scope':'Files and packed G/A verified; does not claim visual/game verification.'}
def make_blk(pairs):
    return 'name:t="user"\n\n'+''.join(f'replace_tex{{\n from:t="{a}"\n to:t="{b}"\n}}\n\n' for a,b in pairs)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',default=str(DEFAULT_CONFIG))
    sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('configure');q.add_argument('--library',required=True);q.add_argument('--game',required=True);q.add_argument('--blender',required=True);q.add_argument('--dae-root');q.add_argument('--dae-python');q.add_argument('--replace',action='store_true')
    sub.add_parser('doctor');sub.add_parser('list')
    q=sub.add_parser('inspect');q.add_argument('image')
    q=sub.add_parser('extract');q.add_argument('--recipe',required=True);q.add_argument('--out',required=True)
    q=sub.add_parser('register');q.add_argument('--id',required=True);q.add_argument('--model',required=True);q.add_argument('--color',required=True);q.add_argument('--normal',required=True);q.add_argument('--material',action='append',required=True);q.add_argument('--color-target',required=True);q.add_argument('--normal-target',required=True);q.add_argument('--baseline')
    q=sub.add_parser('new-order');q.add_argument('--vehicle',required=True);q.add_argument('--id',required=True);q.add_argument('--art',required=True);q.add_argument('--theme',required=True)
    q=sub.add_parser('choose');q.add_argument('--order',required=True);q.add_argument('--image',required=True);q.add_argument('--decision',required=True);q.add_argument('--decided-by',choices=['user','agent-authorized'],default='user')
    q=sub.add_parser('concept-brief');q.add_argument('--order',required=True)
    q=sub.add_parser('baseline');q.add_argument('--vehicle',required=True);q.add_argument('--out',required=True)
    for name in ['preview','bake']:
        q=sub.add_parser(name);q.add_argument('--order',required=True);q.add_argument('--out',required=True);q.add_argument('--size',type=int,default=4096)
    q=sub.add_parser('validate');q.add_argument('package')
    q=sub.add_parser('install');q.add_argument('package');q.add_argument('--skin-name',required=True)
    a=p.parse_args(argv)
    if a.cmd=='configure':
        cp=Path(a.config).expanduser()
        if cp.exists() and not a.replace:raise FileExistsError('Environment exists; use --replace intentionally.')
        c={'schema_version':1,'library':str(Path(a.library).resolve()),'game_root':str(Path(a.game).resolve()),'blender':str(Path(a.blender).resolve()),'dae_root':str(Path(a.dae_root).resolve()) if a.dae_root else None,'dae_python':str(Path(a.dae_python).resolve()) if a.dae_python else sys.executable}
        for key in ['game_root','blender']:
            if not Path(c[key]).exists():raise FileNotFoundError(c[key])
        write(cp,c);return {'configured':str(cp),'library':c['library']}
    if a.cmd=='inspect':return image_info(a.image)
    if a.cmd=='validate':return validate_package(a.package)
    c=config(a)
    if a.cmd=='doctor':
        return {'config':a.config,**c,'exists':{k:bool(v and Path(v).exists()) for k,v in c.items() if k in ['library','game_root','blender','dae_root','dae_python']},'python_modules':{m:bool(importlib.util.find_spec(m)) for m in ['PIL','numpy']}}
    if a.cmd=='list':return {k:[x.parent.name for x in (Path(c['library'])/k).glob('*/'+f)] for k,f in [('vehicles','vehicle.json'),('orders','order.json')]}
    if a.cmd=='extract':
        if not c.get('dae_root'):raise ValueError('Configure an existing Dagor Asset Explorer source checkout first.')
        dest=newdir(a.out);job={'environment':c,'recipe':read(a.recipe),'out':str(dest)};write(dest/'extract-job.json',job)
        run_logged([c['dae_python'],PLUGIN/'scripts'/'dae_export.py',dest/'extract-job.json'],dest/'extract.log')
        if not (dest/'extraction.json').exists():raise RuntimeError('No extraction record; inspect extract.log')
        return read(dest/'extraction.json')
    if a.cmd=='register':
        identifier(a.id);ci=image_info(a.color);ni=image_info(a.normal)
        if ci['flat_rgb']:raise ValueError('Source color is uniform; extract real source texture before registering.')
        if ni['mode']!='RGBA':raise ValueError('Source normal must retain its alpha channel.')
        out=newdir(Path(c['library'])/'vehicles'/a.id)
        for name,source in [('model'+Path(a.model).suffix,a.model),('original/color'+Path(a.color).suffix,a.color),('original/normal'+Path(a.normal).suffix,a.normal)]:copy(source,out/name)
        mtl=Path(a.model).with_suffix('.mtl')
        if mtl.exists():copy(mtl,out/mtl.name)
        if a.baseline:copy(a.baseline,out/'baseline.blend')
        v={'schema_version':1,'id':a.id,'model':'model'+Path(a.model).suffix,'baseline':'baseline.blend' if a.baseline else None,'import_axes':{'forward':'NEGATIVE_Z','up':'Y'},'paint_sets':[{'id':'main','materials':a.material,'color':'original/color'+Path(a.color).suffix,'normal':'original/normal'+Path(a.normal).suffix,'color_target':a.color_target,'normal_target':a.normal_target,'normal_x':'G','normal_y':'A','invert_y':False}], 'cull_material_patterns':['dynamic_null','gunfire','jet_flame','propmask'],'camera_target':[2,0,.5],'camera_scale':26,'validation':{'registered':stamp(),'geometry':'not-yet-checked','uv':'not-yet-checked','game':'not-yet-checked'}}
        write(out/'vehicle.json',v);write(out/'source-provenance.json',{'model':{'path':str(Path(a.model).resolve()),'sha256':digest(a.model)},'color':ci,'normal':ni});return {'vehicle':str(out/'vehicle.json')}
    if a.cmd=='new-order':
        vp,v=vehicle(c,a.vehicle);out=newdir(Path(c['library'])/'orders'/identifier(a.id));copy(a.art,out/'assets'/Path(a.art).name)
        data=read(PLUGIN/'skills/war-thunder-skins/assets/order-template.json');data.update({'id':a.id,'vehicle':v['id'],'theme':a.theme,'art':'assets/'+Path(a.art).name,'created':stamp()});write(out/'order.json',data);return {'order':str(out/'order.json'),'next':'Concept paintovers; no production design chosen.'}
    if a.cmd in ['choose','concept-brief','preview','bake']:
        op,o=order(c,a.order);vp,v=vehicle(c,o['vehicle'])
        if a.cmd=='choose':
            dest=op.parent/'concepts'/Path(a.image).name
            if dest.exists() and digest(dest)!=digest(a.image):raise FileExistsError(dest)
            if not dest.exists():copy(a.image,dest)
            o['concept']={'selected':str(dest.relative_to(op.parent)),'decision':a.decision,'decided_by':a.decided_by,'at':stamp()};write(op,o);return o['concept']
        if a.cmd=='concept-brief':
            return {'theme':o['theme'],'art':str(resolve(op.parent,o['art'])),'vehicle':str(vp),'concept':o['concept'],'directions':o['directions'],'workflow':'Use ImageGen with model baselines + original art. One call per distinct concept. No bake, no install. Label concepts; keep original airframe and character identity, require large visual anchor. Generated multiview consistency is approximate; validate on real mesh after selection.'}
        if not o.get('concept',{}).get('selected'):
            raise ValueError('Record the selected concept with choose before production preview/bake. A test fixture may record an explicitly authorized test design.')
        result=blender(c,{'mode':a.cmd,'vehicle':str(vp),'order':str(op),'size':a.size},a.out)
        if a.cmd=='bake':result['validation']=validate_package(Path(a.out)/'package')
        return result
    if a.cmd=='baseline':
        vp,v=vehicle(c,a.vehicle);return blender(c,{'mode':'baseline','vehicle':str(vp)},a.out)
    if a.cmd=='install':
        validate_package(a.package);target=inside(Path(c['game_root'])/'UserSkins',identifier(a.skin_name))
        if target.exists():raise FileExistsError(f'Existing skin retained; choose a new name: {target}')
        target.parent.mkdir(parents=True,exist_ok=True)
        # Prevalidated copy in a staging directory; only rename to the visible skin on success.
        stage=Path(tempfile.mkdtemp(prefix='.studio-stage-',dir=target.parent))
        try:
            src=Path(a.package);manifest=read(src/'package.json')
            for e in manifest['textures']:copy(src/e['file'],stage/e['file'])
            copy(src/(manifest['vehicle']+'.blk'),stage/(manifest['vehicle']+'.blk'))
            write(stage/'validation.json',{'file_validation':True,'installed_at':stamp(),'game_validation':'pending','files':{p.name:digest(p) for p in stage.iterdir() if p.suffix in ['.tga','.dds','.blk']}})
            stage.rename(target)
        except Exception:
            # Only remove our freshly created staging directory within UserSkins.
            if stage.exists() and stage.resolve().parent==target.parent.resolve():shutil.rmtree(stage)
            raise
        return {'installed':str(target),'game_validation':'pending'}

if __name__=='__main__':
    try:print(json.dumps(main(),ensure_ascii=False,indent=2))
    except (ValueError,FileNotFoundError,FileExistsError,KeyError,RuntimeError,subprocess.TimeoutExpired) as e:
        print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(1)
