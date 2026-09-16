"""Blender-only worker. Inputs are versioned JSON jobs produced by studio.py."""
import bpy,bmesh,json,sys,math,subprocess
from pathlib import Path
from mathutils import Vector
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from studio import read,write,resolve,digest,identifier,make_blk

job=read(sys.argv[sys.argv.index('--')+1]);outdir=Path(job['out']);vp=Path(job['vehicle']);v=read(vp)
op=Path(job['order']) if job.get('order') else None;o=read(op) if op else {'layers':[],'finish':{}}
mode=job['mode'];assetbase=op.parent if op else vp.parent
baseline=resolve(vp.parent,v['baseline']) if v.get('baseline') else None
if baseline and baseline.exists():bpy.ops.wm.open_mainfile(filepath=str(baseline))
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    model=resolve(vp.parent,v['model'])
    if model.suffix.lower()!='.obj':raise ValueError('Generic import currently supports OBJ; use a registered baseline.blend for other formats.')
    axes=v.get('import_axes',{});bpy.ops.wm.obj_import(filepath=str(model),forward_axis=axes.get('forward','NEGATIVE_Z'),up_axis=axes.get('up','Y'))
scene=bpy.context.scene;meshes=[ob for ob in scene.objects if ob.type=='MESH']
for ob in meshes:
    bad={i for i,ma in enumerate(ob.data.materials) if ma and any(p in ma.name for p in v.get('cull_material_patterns',[]))}
    if bad:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index in bad],context='FACES');bm.to_mesh(ob.data);bm.free()
    if not ob.data.uv_layers:raise ValueError(f'No UVs: {ob.name}')

class Graph:
    def __init__(self,mat,ps):
        self.mat=mat;self.ps=ps;mat.use_nodes=True;self.nt=mat.node_tree;self.nt.nodes.clear()
        geo=self.node('ShaderNodeNewGeometry');self.pos=geo.outputs['Position'];self.normal=geo.outputs['Normal']
        orig=self.image(resolve(vp.parent,ps['color']));self.color=orig.outputs['Color']
        packed=self.image(resolve(vp.parent,ps['normal']),data=True)
        sep=self.node('ShaderNodeSeparateColor');self.link(packed.outputs['Color'],sep.inputs[0])
        channels={'R':sep.outputs[0],'G':sep.outputs[1],'B':sep.outputs[2],'A':packed.outputs['Alpha']}
        self.rough=self.math('SUBTRACT',1,channels['R']);self.metal=channels['B'];self.paint=0
        for layer in o.get('layers',[]):
            if layer.get('set','main')==ps['id']:self.layer(layer)
        xx=channels[ps.get('normal_x','G')];yy=channels[ps.get('normal_y','A')]
        if ps.get('invert_y'):yy=self.math('SUBTRACT',1,yy)
        x2=self.math('POWER',self.math('SUBTRACT',self.math('MULTIPLY',xx,2),1),2)
        y2=self.math('POWER',self.math('SUBTRACT',self.math('MULTIPLY',yy,2),1),2)
        zz=self.math('ADD',.5,self.math('MULTIPLY',.5,self.math('SQRT',self.math('MAXIMUM',self.math('SUBTRACT',1,self.math('ADD',x2,y2)),0))))
        nm=self.node('ShaderNodeNormalMap');self.link(self.vector(xx,yy,zz),nm.inputs['Color'])
        self.bs=self.node('ShaderNodeBsdfPrincipled');self.link(self.color,self.bs.inputs['Base Color']);self.link(self.rough,self.bs.inputs['Roughness']);self.link(self.metal,self.bs.inputs['Metallic']);self.link(nm.outputs[0],self.bs.inputs['Normal'])
        self.bs.inputs['Coat Weight'].default_value=o.get('finish',{}).get('preview_coat',0)
        self.bs.inputs['Coat Roughness'].default_value=.2
        self.output=self.node('ShaderNodeOutputMaterial');self.link(self.bs.outputs[0],self.output.inputs[0])
    def node(self,t):return self.nt.nodes.new(t)
    def link(self,a,b):
        if hasattr(a,'node'):self.nt.links.new(a,b)
        else:b.default_value=a
    def math(self,op,a,b=0):
        n=self.node('ShaderNodeMath');n.operation=op;self.link(a,n.inputs[0]);self.link(b,n.inputs[1]);return n.outputs[0]
    def vector(self,x,y,z=0):
        n=self.node('ShaderNodeCombineXYZ')
        for i,t in enumerate((x,y,z)):self.link(t,n.inputs[i])
        return n.outputs[0]
    def dot(self,s,axis):
        n=self.node('ShaderNodeVectorMath');n.operation='DOT_PRODUCT';self.link(s,n.inputs[0]);n.inputs[1].default_value=axis;return n.outputs['Value']
    def image(self,path,data=False,coords=None):
        n=self.node('ShaderNodeTexImage');n.image=bpy.data.images.load(str(path),check_existing=True)
        if data:n.image.colorspace_settings.name='Non-Color';n.image.alpha_mode='CHANNEL_PACKED'
        if coords is not None:n.extension='CLIP';self.link(coords,n.inputs['Vector'])
        return n
    def mix(self,a,b,f):
        n=self.node('ShaderNodeMixRGB');self.link(f,n.inputs[0]);self.link(a,n.inputs[1]);self.link(b,n.inputs[2]);return n.outputs[0]
    def scalar_mix(self,a,b,f):return self.math('ADD',self.math('MULTIPLY',a,self.math('SUBTRACT',1,f)),self.math('MULTIPLY',b,f))
    def mask(self,spec):
        f=1
        if spec.get('normal'):
            direction=Vector(spec['normal'])
            if direction.length==0:raise ValueError('Mask normal must be nonzero')
            f=self.math('GREATER_THAN',self.dot(self.normal,list(direction.normalized())),spec.get('min_dot',.2))
        for axis,rng in spec.get('bounds',{}).items():
            ax={'x':[1,0,0],'y':[0,1,0],'z':[0,0,1]}[axis];s=self.dot(self.pos,ax)
            f=self.math('MULTIPLY',f,self.math('MULTIPLY',self.math('GREATER_THAN',s,rng[0]),self.math('LESS_THAN',s,rng[1])))
        return self.math('MULTIPLY',f,spec.get('opacity',1))
    def layer(self,l):
        f=self.mask(l.get('mask',{}));kind=l['type']
        if kind=='solid':col=l['color']
        elif kind=='band':
            # Affine band in world space; complex custom ornament is supplied as a separate transparent asset.
            s=self.math('ADD',self.dot(self.pos,l['axis']),l.get('offset',0))
            f=self.math('MULTIPLY',f,self.math('LESS_THAN',self.math('ABSOLUTE',s),l['half_width']));col=l['color']
        elif kind=='image':
            origin=Vector(l['origin']);u=Vector(l['u_axis']);vv=Vector(l['v_axis']);size=l['size']
            if min(size)<=0 or abs(u.length-1)>.001 or abs(vv.length-1)>.001 or abs(u.dot(vv))>.001:raise ValueError('Projection axes must be perpendicular unit vectors; size must be positive')
            us=self.math('DIVIDE',self.math('SUBTRACT',self.dot(self.pos,list(u)),origin.dot(u)),size[0])
            vs=self.math('DIVIDE',self.math('SUBTRACT',self.dot(self.pos,list(vv)),origin.dot(vv)),size[1])
            for s in [us,vs]:f=self.math('MULTIPLY',f,self.math('MULTIPLY',self.math('GREATER_THAN',s,0),self.math('LESS_THAN',s,1)))
            cr=l.get('crop',[0,0,1,1]);uc=self.math('ADD',cr[0],self.math('MULTIPLY',us,cr[2]-cr[0]));vc=self.math('ADD',cr[1],self.math('MULTIPLY',vs,cr[3]-cr[1]))
            im=self.image(resolve(assetbase,l['image']),coords=self.vector(uc,vc));f=self.math('MULTIPLY',f,im.outputs['Alpha']);col=im.outputs['Color']
        else:raise ValueError(f'Unsupported layer: {kind}')
        self.color=self.mix(self.color,col,f);self.paint=self.math('MAXIMUM',self.paint,f)
        self.rough=self.scalar_mix(self.rough,l.get('roughness',o.get('finish',{}).get('roughness',.3)),f)
        self.metal=self.scalar_mix(self.metal,l.get('metalness',o.get('finish',{}).get('metalness',0)),f)

groups=[]
for ps in v['paint_sets']:
    identifier(ps['id']);members=[];originals=[]
    for ob in meshes:
        ids=[i for i,ma in enumerate(ob.data.materials) if ma and ma.name in ps['materials']]
        if ids:members.append((ob,ids))
    if not members:raise ValueError(f'No exact material matches for {ps["id"]}: {ps["materials"]}')
    mat=bpy.data.materials.new('Studio_'+ps['id']);mat.use_fake_user=True;graph=Graph(mat,ps)
    for ob,ids in members:
        for i in ids:ob.data.materials[i]=mat
    groups.append((ps,members,graph))

target=Vector(v.get('camera_target',[0,0,0]));scale=v.get('camera_scale',26)
for ob in list(scene.objects):
    if ob.type in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
scene.world=bpy.data.worlds.new('Studio Neutral');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.18,.23,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((4,-9,16),2400,12),((-7,7,10),2200,9),((8,10,6),1400,8)]:
    bpy.ops.object.light_add(type='AREA',location=target+Vector(loc));ob=bpy.context.object;ob.data.energy=power;ob.data.size=size;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=target+Vector((0,0,36)));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=scale;scene.camera=cam
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'

if mode=='bake':
    size=int(job['size'])
    if size<64 or size>8192 or size&(size-1):raise ValueError('Bake size must be a power of two from 64 to 8192')
    pkg=outdir/'package';pkg.mkdir();entries=[]
    scene.render.engine='CYCLES';scene.cycles.samples=1;scene.render.bake.margin=12
    for ps,members,g in groups:
        temporary=[]
        for ob,ids in members:
            dup=ob.copy();dup.data=ob.data.copy();scene.collection.objects.link(dup)
            bm=bmesh.new();bm.from_mesh(dup.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index not in ids],context='FACES')
            for f in bm.faces:f.material_index=0
            bm.to_mesh(dup.data);bm.free();dup.data.materials.clear();dup.data.materials.append(g.mat);temporary.append(dup)
        emit=g.node('ShaderNodeEmission');g.link(emit.outputs[0],g.output.inputs[0])
        def bake(name,signal,wh,data=False):
            im=bpy.data.images.new(name,width=wh[0],height=wh[1],alpha=False)
            if data:im.colorspace_settings.name='Non-Color'
            n=g.node('ShaderNodeTexImage');n.image=im;g.nt.nodes.active=n;g.link(signal,emit.inputs[0])
            for idx,ob in enumerate(temporary):
                bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;scene.render.bake.use_clear=(idx==0);bpy.ops.object.bake(type='EMIT')
            return im
        name=identifier(v['id'])+'_'+ps['id'];color=bake(name,g.color,(size,size))
        color.filepath_raw=str(pkg/(name+'_c.tga'));color.file_format='TARGA';color.save()
        src=resolve(vp.parent,ps['normal']);wh=tuple(bpy.data.images.load(str(src),check_existing=True).size)
        controls=bake(name+'_controls',g.vector(g.math('SUBTRACT',1,g.rough),g.metal,g.paint),wh,True)
        pixels=np.empty(wh[0]*wh[1]*4,dtype=np.float32);controls.pixels.foreach_get(pixels);np.save(outdir/(name+'_controls.npy'),pixels.reshape(wh[1],wh[0],4))
        nf=pkg/(name+'_n.tga')
        subprocess.run([job['python'],str(Path(__file__).with_name('pack_normal.py')),str(src),str(outdir/(name+'_controls.npy')),str(nf)],check=True)
        entries.extend([{'file':color.filepath_raw and Path(color.filepath_raw).name,'from':ps['color_target'],'role':'color','sha256':digest(color.filepath_raw),'allow_flat':o.get('allow_flat_color',False)},{'file':nf.name,'from':ps['normal_target'],'role':'normal','normal_source':str(src),'sha256':digest(nf)}])
        for dup in temporary:bpy.data.objects.remove(dup,do_unlink=True)
        g.link(g.bs.outputs[0],g.output.inputs[0])
        # Rebuild from exported files and no spatial layers, so QA sees exactly the package textures.
        exportps=dict(ps,color=str(pkg/(name+'_c.tga')),normal=str(nf))
        saved=o.get('layers',[]);o['layers']=[]
        exported=bpy.data.materials.new('Exported_'+ps['id']);Graph(exported,exportps);o['layers']=saved
        for ob,ids in members:
            for i in ids:ob.data.materials[i]=exported
    (pkg/(identifier(v['id'])+'.blk')).write_text(make_blk([(e['from'],e['file']) for e in entries]),encoding='utf-8')
    write(pkg/'package.json',{'schema_version':1,'vehicle':v['id'],'order':o['id'],'textures':entries,'scope':'Main registered paint sets; no unverified damage substitutions.'})
    scene.render.engine='BLENDER_EEVEE'

views=[('top',(0,0,36)),('angle',(21,-24,27)),('side',(0,-36,4))]
if mode=='bake':views.extend([('other-side',(0,36,4)),('belly',(0,0,-36))])
for label,offset in views:
    cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(outdir/(label+'.png'));bpy.ops.render.render(write_still=True)
for im in bpy.data.images:
    if im.has_data:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(outdir/'scene.blend'))
inventory={'meshes':len(meshes),'faces':sum(len(ob.data.polygons) for ob in meshes),'uv_layers':{ob.name:len(ob.data.uv_layers) for ob in meshes},'paint_sets':[p['id'] for p,_,_ in groups]}
write(outdir/'result.json',{'ok':True,'mode':mode,'vehicle':v['id'],'order':o.get('id'),'inventory':inventory,'views':[label+'.png' for label,_ in views],'scene':'scene.blend','game_verified':False})
