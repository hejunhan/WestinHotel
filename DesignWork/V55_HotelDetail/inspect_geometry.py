import bpy, bmesh, json, numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
O=Path('C:/Users/Lenovo/WestinHotel/DesignWork/V55_HotelDetail')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(O/'Audit/dongshuhe_F3.fbx'))
out=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 arr=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])
 print('FBX BOUNDS',ob.name,arr.min(0),arr.max(0),len(arr),len(ob.data.polygons),'matrix',ob.matrix_world)
 np.savez_compressed(O/'Audit/f3_raw.npz',vertices=arr,triangles=np.array([list(p.vertices) for p in ob.data.polygons]))
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005);bm.verts.ensure_lookup_table()
 seen=set();parts=[]
 for v in bm.verts:
  if v in seen:continue
  comp={v}; todo=[v];seen.add(v)
  while todo:
   a=todo.pop()
   for e in a.link_edges:
    q=e.other_vert(a)
    if q not in seen:seen.add(q);comp.add(q);todo.append(q)
  pts=np.array([tuple(ob.matrix_world@v.co) for v in comp]); faces={f for v in comp for f in v.link_faces}
  parts.append({'min':pts.min(0).tolist(),'max':pts.max(0).tolist(),'verts':len(comp),'faces':len(faces)})
 out.extend(parts)
 print('PARTS',len(parts))
(O/'Audit/components_raw.json').write_text(json.dumps(out,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Audit/Hotel_AsRead.blend'))
