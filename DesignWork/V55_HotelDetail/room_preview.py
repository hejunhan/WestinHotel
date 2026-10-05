import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
O=Path('C:/Users/Lenovo/WestinHotel/DesignWork/V55_HotelDetail')
L=json.loads((O/'Source/library.json').read_text(encoding='utf8'))
for item in L['placements']:
 if item['id'] in ['04','09']:item['yaw']=-90
(O/'Source/library.json').write_text(json.dumps(L,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(O/'Audit/Hotel_AsRead.blend'))
ob=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005);bm.verts.ensure_lookup_table()
seen=set();comps=[]
for v in bm.verts:
 if v in seen:continue
 comp={v};todo=[v];seen.add(v)
 while todo:
  a=todo.pop()
  for e in a.link_edges:
   q=e.other_vert(a)
   if q not in seen:seen.add(q);comp.add(q);todo.append(q)
 comps.append(comp)
REMOVE=[128,139,333,339,367,438,1016,1033,1035,1042,1045,1054,1057,1059,1060,1061]
faces={f for i in REMOVE for v in comps[i] for f in v.link_faces}
audit={'remove_component_ids':REMOVE,'removed_faces':len(faces),'removed_components':len(REMOVE),'original_mesh_unchanged':True,'reason':'Only replace obsolete 307 bed, sofa, coffee table, chair, bedside and shoe bench; preserve structure, book, desk, wardrobe and bathroom.'}
(O/'Audit/proposed_shell_copy.json').write_text(json.dumps(audit,indent=2))
bmesh.ops.delete(bm,geom=list(faces),context='FACES')
# Original source vertices are centimeters because imported FBX matrix is .01.
bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
payload={'name':'SM_H55_HotelShell307','vertices_cm':[[v.co.x,-v.co.y,v.co.z] for v in bm.verts],'faces':[list(reversed([v.index for v in f.verts])) for f in bm.faces]}
# UV source already exists; include loop values unchanged, reverse with winding.
uv=bm.loops.layers.uv.active
payload['uvs']=[list(reversed([list(loop[uv].uv) for loop in f.loops])) for f in bm.faces]
(O/'Source/Shell307_candidate.json').write_text(json.dumps(payload,separators=(',',':')))
bm.to_mesh(ob.data);bm.free()
# Preview local room coordinates, Z up, +Y north; preserve original dimensions.
for v in ob.data.vertices:
 raw=ob.matrix_world@v.co
 v.co=((raw.x*100+14615.131025-19022.306)/100,-(raw.z*100+457.395898-692.402)/100,(raw.y*100+4766.847454-7083.445)/100)
ob.matrix_world.identity();ob.data.materials.clear();ob.color=(.52,.51,.47,1);ob.name='Existing_shell_cutaway_PREVIEW_ONLY'
bm=bmesh.new();bm.from_mesh(ob.data)
for pt,no in [((-.15,0,0),(-1,0,0)),((11.42,0,0),(1,0,0)),((0,.15,0),(0,1,0)),((0,-13.8,0),(0,-1,0)),((0,0,2.4),(0,0,1)),((0,0,-.1),(0,0,-1))]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=pt,plane_no=no,clear_outer=True,dist=.00001)
bm.to_mesh(ob.data);bm.free()
COLORS={'Wood':(.26,.19,.13,1),'Metal':(.08,.09,.085,1),'Fabric':(.39,.42,.32,1),'Stone':(.52,.51,.46,1),'Default':(.62,.61,.57,1)}
for it in L['placements']:
 for pn in L['models'][it['model']]['parts']:
  d=json.loads((O/'Source'/(pn+'.json')).read_text());verts=[(v[0]/100,-v[1]/100,v[2]/100) for v in d['vertices_cm']];faces=[list(reversed(f)) for f in d['faces']]
  me=bpy.data.meshes.new(pn);me.from_pydata(verts,[],faces);me.update();n=bpy.data.objects.new(it['id']+'_'+pn,me);bpy.context.collection.objects.link(n);n.location=(it['x']+it['w']/2,-it['y']-it['d']/2,0);n.rotation_euler.z=-math.radians(it['yaw']);n.color=COLORS[d['role']]
  for poly in me.polygons:poly.use_smooth=True
# Keep original movable wardrobe as a separately displayed existing volume.
bpy.ops.mesh.primitive_cube_add(size=1,location=(.461,-5.7716,1.6981));ward=bpy.context.object;ward.name='Existing_movable_wardrobe_REFERENCE';ward.dimensions=(.82,2.8,3.4);ward.color=(.24,.18,.13,1)
sc=bpy.context.scene
if not sc.world:sc.world=bpy.data.worlds.new('PreviewWorld')
sc.world.color=(.6,.6,.6);sc.render.engine='BLENDER_WORKBENCH';sh=sc.display.shading;sh.light='STUDIO';sh.color_type='OBJECT';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD'
bpy.ops.object.camera_add(location=(18,8,21));cam=bpy.context.object;cam.rotation_euler=(Vector((5.5,-6.7,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=20;sc.camera=cam
sc.render.resolution_x=1500;sc.render.resolution_y=1500;sc.render.resolution_percentage=100;sc.render.filepath=str(O/'Preview/307_furnished_cutaway.png');bpy.ops.render.render(write_still=True)
cam.location=(5.635,-6.825,30);cam.rotation_euler=(0,0,0);cam.rotation_euler=(Vector((5.635,-6.825,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=15;sc.render.filepath=str(O/'Preview/307_furnished_top.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Source/V55_307_Layout_Preview.blend'))
print('ROOM_PREVIEW_COMPLETE',audit)
