import bpy,bmesh,json,math,os
from pathlib import Path
from mathutils import Vector
O=Path('C:/Users/Lenovo/WestinHotel/DesignWork/V55_HotelDetail')
for p in ['Source','Exports','Preview','Audit']:(O/p).mkdir(exist_ok=True)
PLAN=json.loads((O/'Source/V50_plan_reference.json').read_text(encoding='utf8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
COL=bpy.data.collections.new('V55_Furniture_Master');scene.collection.children.link(COL)
parts=[];models={};qa=[]
COLORS={'Wood':(.26,.19,.13,1),'Metal':(.08,.09,.085,1),'Fabric':(.39,.42,.32,1),'Stone':(.52,.51,.46,1),'Default':(.62,.61,.57,1)}
def active(ob):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
def box(n,center,size,role='Wood',bevel=.009,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);ob=bpy.context.object;ob.name=n;ob.dimensions=size;ob.rotation_euler.z=rot
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=ob.modifiers.new('Manufactured edge radius','BEVEL');m.width=bevel;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name)
 ob['Role']=role;ob.color=COLORS[role];parts.append(ob);return ob
def rod(n,a,b,r,role='Metal'):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2)
 ob=bpy.context.object;ob.name=n;ob.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 ob['Role']=role;ob.color=COLORS[role];parts.append(ob);return ob
def framelegs(w,d,z,top=.04):
 for x in [-w/2+.08,w/2-.08]:
  for y in [-d/2+.075,d/2-.075]:box('Solid leg',(x,y,z/2),(.055,.055,z+.01),'Metal',.006)
 box('Front apron',(0,-d/2+.08,z-.05),(w-.1,.035,.09),'Metal',.004)
 box('Rear apron',(0,d/2-.08,z-.05),(w-.1,.035,.09),'Metal',.004)
def cabinet(w,d,h,doors=2,open_top=False):
 # Folded carcass is Boolean united into a closed coherent mesh below.
 box('Recessed plinth',(0,0,.06),(w-.14,d-.12,.12),'Metal',.007)
 for x in [-w/2+.022,w/2-.022]:box('Carcass side',(x,0,(h+.12)/2),(.044,d,h-.12))
 for z in [.145,h-.022]:box('Carcass horizontal',(0,0,z),(w,d,.044))
 box('Carcass back',(0,d/2-.018,(h+.12)/2),(w,.036,h-.12))
 if not open_top:
  for i in range(doors):
   dw=(w-.032)/doors;x=-w/2+.016+dw*(i+.5)
   box('Panel door',(x,-d/2-.025,(h+.17)/2),(dw-.008,.032,h-.18),'Wood',.004)
   rod('Pull', (x+dw/2-.09,-d/2-.028,h*.45),(x+dw/2-.09,-d/2-.028,h*.62),.009)
 else:
  for z in [.55,1.02,1.48]:
   if z<h-.1:box('Display shelf',(0,-.01,z),(w-.065,d-.04,.03),'Wood',.003)
def bench(w,d):
 framelegs(w,d,.36);box('Bench deck',(0,0,.365),(w,d,.055),'Wood',.012)
 box('Upholstered seat',(0,0,.425),(w-.035,d-.02,.09),'Fabric',.035)
def lounge(w=2.8,d=.9):
 framelegs(w,d,.22)
 box('Sofa base',(0,0,.245),(w-.035,d-.03,.14),'Wood',.025)
 for x in [-w/2+.09,w/2-.09]:
  box('Solid side frame',(x,0,.44),(.13,d,.41),'Wood',.025)
  box('Arm cap',(x,-.015,.665),(.19,d-.01,.06),'Wood',.022)
 box('Back frame',(0,d/2-.065,.535),(w-.17,.11,.51),'Wood',.017)
 count=3 if w>1.8 else 1
 for i in range(count):
  sw=(w-.4)/count;x=-(w-.4)/2+sw*(i+.5)
  box('Seat cushion',(x,-.035,.4),(sw-.015,d-.23,.19),'Fabric',.047)
  ob=box('Back cushion',(x,d/2-.19,.638),(sw-.015,.175,.37),'Fabric',.045);ob.rotation_euler.x=math.radians(-9)
def table(w,d,h):
 framelegs(w-.06,d-.035,h-.065);box('Table top',(0,0,h-.03),(w,d,.06),'Wood',.02)
def start():parts.clear()
def finish(name,description,union_structure=False):
 byrole={}
 for ob in parts:byrole.setdefault(ob['Role'],[]).append(ob)
 finished=[]
 for role,obs in byrole.items():
  # Boolean union only touching structural members; cushions remain separately closed solids.
  if role in ['Wood','Metal'] and union_structure and len(obs)>1:
   base=obs[0];active(base);survivors=[]
   for ob in obs[1:]:
    mod=base.modifiers.new('Join manufactured structure','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=ob
    try:bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(ob,do_unlink=True)
    except:base.modifiers.remove(mod);survivors.append(ob)
   obs=[base]+survivors
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:
   mb=bmesh.new();mb.from_mesh(ob.data);bmesh.ops.remove_doubles(mb,verts=list(mb.verts),dist=.000003);bmesh.ops.recalc_face_normals(mb,faces=list(mb.faces));mb.to_mesh(ob.data);mb.free()
   ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  ob=obs[0];ob.name=name+'_'+role
  if role in ['Wood','Metal'] and union_structure:
   bevel=ob.modifiers.new('Unified edge treatment','BEVEL');bevel.width=.004;bevel.segments=3;bevel.use_clamp_overlap=True
   bpy.ops.object.modifier_apply(modifier=bevel.name)
  bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  bm=bmesh.new();bm.from_mesh(ob.data);pre=len(bm.verts)
  # Weld each manufactured component before combining, never collapse separate contacting panels.
  bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
  bmesh.ops.delete(bm,geom=[e for e in bm.edges if e.is_wire],context='EDGES')
  bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
  edgeholes=[e for e in bm.edges if e.is_boundary]
  if edgeholes:
   print('REPAIR boundary seams',ob.name,len(edgeholes),sum(e.calc_length() for e in edgeholes))
   bmesh.ops.holes_fill(bm,edges=edgeholes,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
  boundaries=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-12 for f in bm.faces)
  assert not boundaries and not nonmanifold and not zero,(ob.name,boundaries,nonmanifold,zero)
  bm.to_mesh(ob.data);bm.free();ob.data.update()
  active(ob);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
  for p in ob.data.polygons:p.use_smooth=True
  mod=ob.modifiers.new('Weighted manufactured normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
  bpy.ops.object.modifier_apply(modifier=mod.name)
  for c in list(ob.users_collection):c.objects.unlink(ob)
  COL.objects.link(ob);ob['Role']=role;ob['Furniture']=name;ob.color=COLORS[role]
  mesh=ob.data;uv=mesh.uv_layers.active.data
  payload={'name':ob.name,'furniture':name,'role':role,'vertices_cm':[[c*100 for c in v.co] for v in mesh.vertices],'faces':[list(p.vertices) for p in mesh.polygons],'uvs':[[list(uv[i].uv) for i in p.loop_indices] for p in mesh.polygons]}
  (O/'Source'/(ob.name+'.json')).write_text(json.dumps(payload,separators=(',',':')),encoding='utf8')
  qa.append({'mesh':ob.name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'welded_vertices':pre-len(mesh.vertices),'boundary_edges':boundaries,'non_manifold_edges':nonmanifold,'zero_area_faces':zero,'material_role':role})
  finished.append(ob.name)
 models[name]={'description':description,'parts':finished}

start();cabinet(2.3,.6,2.4,3);finish('H55_EntryWardrobe','三门衣帽柜：内凹踢脚、实木门板、金属拉手')
start();bench(1.4,.6);finish('H55_LuggageBench','玄关换鞋及行李凳')
start()
for x in [-.067,.067]:box('Screen stile',(x,0,1.15),(.026,2.05,2.3),'Wood',.006) if False else None
for y in [-1.0,1.0]:box('Screen end',(0,y,1.15),(.16,.05,2.3),'Wood',.007)
for z in [.06,2.26]:box('Screen rail',(0,0,z),(.16,2.05,.08),'Wood',.007)
for i in range(12):box('Vertical timber louver',(0,-.935+i*.17,1.15),(.10,.045,2.18),'Wood',.006,math.radians(12))
finish('H55_EntryScreen','2.3m竖向木格屏风，遮床但透视')
start();cabinet(1.7,.6,.87,3);box('Tea worktop',(0,0,.895),(1.7,.6,.05),'Stone',.009)
box('Minibar ventilation',(0,-.321,.27),(.43,.012,.18),'Metal',.002)
for i in range(6):box('Vent groove',(0,-.331,.205+i*.026),(.39,.014,.009),'Metal',.001)
finish('H55_TeaCabinet','茶水台及通风小冰箱柜')
start();lounge();finish('H55_Sofa','三座木框沙发，分块圆角软包')
start();table(1.4,.75,.42);box('Lower shelf',(0,0,.16),(1.18,.56,.035),'Wood',.01);finish('H55_CoffeeTable','低茶几及下层置物板')
start();lounge(.8,.85);finish('H55_Armchair','同系列木扶手单椅')
start();cabinet(2.2,.4,1.8,open_top=True)
for x in [-.36,.36]:box('Bookcase divider',(x,0,.975),(.032,.34,1.62),'Wood',.004)
# restrained closed book blocks, all six faces connected, no alpha cards
for i in range(7):box('Book spine',(-.93+i*.10,-.06,.73),(.065,.22,.32),'Default',.004)
finish('H55_Bookcase','开放书架：格架、书籍，墙侧排列')
start();framelegs(.60,.61,.43);box('Chair seat',(0,0,.45),(.6,.59,.065),'Fabric',.025)
for x in [-.255,.255]:box('Rear upright',(x,.25,.67),(.045,.045,.63),'Wood',.009)
box('Chair back',(0,.255,.82),(.56,.045,.25),'Wood',.018);finish('H55_DeskChair','书桌配套木背椅')
start()
for z in [.075,1.325]:box('Low screen rail',(0,0,z),(3,.18,.05),'Wood',.007)
for x in [-1.46,1.46]:box('Low screen stile',(x,0,.7),(.08,.18,1.3),'Wood',.007)
for i in range(17):box('Low screen slat',(-1.36+i*.17,0,.7),(.06,.11,1.2),'Wood',.008)
finish('H55_SleepScreen','1.35m低格栅屏风，保留第三人称视野')
start();box('Bed plinth',(0,0,.10),(1.89,1.82,.20),'Metal',.022)
box('Bed frame',(0,0,.235),(2.1,2,.16),'Wood',.024)
box('Mattress',(0,-.012,.415),(2.04,1.93,.20),'Fabric',.075)
box('Headboard',(0,.965,.61),(2.1,.07,.96),'Wood',.017)
for x in [-.48,.48]:box('Pillow',(x,.56,.562),(.83,.49,.13),'Fabric',.062)
box('Folded cover',(0,-.55,.527),(1.99,.71,.035),'Fabric',.016)
finish('H55_DoubleBed','双人床、床架、软包床垫及枕头')
start();cabinet(.5,.6,.55,1);finish('H55_Bedside','床头矮柜')
start();table(1.65,.5,.78)
box('Vanity drawer',(0,-.02,.655),(1.42,.4,.15),'Wood',.008)
rod('Drawer pull',(-.12,-.245,.66),(.12,-.245,.66),.009)
finish('H55_Vanity','梳妆台，不新增镜面材质')
start();bench(1.65,.6);finish('H55_DressingBench','更衣区长凳')
start();cabinet(2.3,.5,.9,3);finish('H55_LinenCabinet','布草收纳矮柜')
mapping={'01':'H55_EntryWardrobe','02':'H55_LuggageBench','03':'H55_EntryScreen','04':'H55_TeaCabinet','05':'H55_Sofa','06':'H55_CoffeeTable','07':'H55_Armchair','08':'H55_Armchair','09':'H55_Bookcase','11':'H55_DeskChair','12':'H55_SleepScreen','13':'H55_DoubleBed','14':'H55_Bedside','15':'H55_Bedside','16':'H55_Vanity','17':'H55_DressingBench','18':'H55_LinenCabinet'}
placements=[]
for item in PLAN['items']:
 if item['id'] not in mapping:continue
 name=mapping[item['id']];angle=-90 if item['id'] in ['04','09'] else 90 if item['id']=='11' else 180 if item['id']=='05' else 0
 # Blender +Y is front-to-back of furniture; UE handedness conversion handled in the export stage.
 placements.append(dict(item,model=name,yaw=angle))
(O/'Source/library.json').write_text(json.dumps({'models':models,'placements':placements,'origin_ue_cm':[19022.306,692.402,7083.445],'retain_original':['task desk and task book','bathroom enclosure and fixtures','movable wardrobe and hidden doorway']},ensure_ascii=False,indent=2),encoding='utf8')
(O/'Audit/blender_topology.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
# Distribute editable master meshes for an asset-sheet view. Export data above remains at origin.
for i,(name,rec) in enumerate(models.items()):
 for pn in rec['parts']:bpy.data.objects[pn].location=((i%5)*3.6,(i//5)*3.6,0)
scene.world=bpy.data.worlds.new('Preview World');scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.4;scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.6,.6,.6)
bpy.ops.object.camera_add(location=(23,-25,23));camera=bpy.context.object;camera.rotation_euler=(Vector((7,4,.3))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=23;scene.camera=camera
scene.render.resolution_x=1700;scene.render.resolution_y=1150;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Source/V55_Hotel_Furniture.blend'))
scene.render.filepath=str(O/'Preview/Furniture_library_clay.png');bpy.ops.render.render(write_still=True)
print('V55_FURNITURE_COMPLETE',len(models),len(qa),len(placements))
