import os,json,math,traceback
from pathlib import Path
O=Path('C:/Users/Lenovo/WestinHotel/DesignWork/V55_HotelDetail')
os.environ['MAYA_APP_DIR']=str(O/'Source/MayaSession')
os.environ['MAYA_DISABLE_CIP']='1'
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as c,maya.api.OpenMaya as om,maya.mel as mel
c.file(new=True,force=True);c.currentUnit(linear='cm');c.upAxis(axis='z',rotateView=True)
c.loadPlugin('fbxmaya',quiet=True)
ROOT=c.group(empty=True,name='V55_HotelFurniture'); report=[]; meshes=[]
for p in sorted((O/'Source').glob('H55_*.json')):
 d=json.loads(p.read_text(encoding='utf8'));name=d['name'];vs=d['vertices_cm'];fs=d['faces'];uvs=d['uvs']
 # Maya Z-up FBX is converted to UE's left-handed frame: preflip Y and winding.
 pts=om.MPointArray([om.MPoint(v[0],-v[1],v[2]) for v in vs]);counts=[len(f) for f in fs];ids=[i for f in fs for i in reversed(f)]
 fn=om.MFnMesh();fn.create(pts,counts,ids);shape=fn.fullPathName();ob=c.listRelatives(shape,parent=True,fullPath=True)[0];ob=c.rename(ob,name)
 sel=om.MSelectionList();sel.add(ob);dag=sel.getDagPath(0);dag.extendToShape();fn=om.MFnMesh(dag)
 flattened=[uv for face in uvs for uv in reversed(face)]
 fn.setUVs([uv[0] for uv in flattened],[uv[1] for uv in flattened]);fn.assignUVs(counts,list(range(len(flattened))))
 c.sets(ob,edit=True,forceElement='initialShadingGroup')
 # Repair within each physical shell, avoiding nonmanifold welds between contacting boards.
 npre=c.polyEvaluate(ob,vertex=True)
 faceiter=om.MItMeshPolygon(dag); visited=set();shells=[];adj=[]
 while not faceiter.isDone():adj.append(list(faceiter.getConnectedFaces()));faceiter.next()
 for k in range(len(fs)):
  if k in visited:continue
  visited.add(k);todo=[k];shell=[]
  while todo:
   j=todo.pop();shell.append(j)
   for n in adj[j]:
    if n not in visited:visited.add(n);todo.append(n)
  shells.append(shell)
 # Vertices are shared by face indices; weld only where real coincident vertices remain per shell.
 weld_count=0
 for shell in shells:
  verts=sorted({v for fi in shell for v in fs[fi]}); seen={};dup=[]
  for vi in verts:
   key=tuple(round(a,4) for a in vs[vi])
   if key in seen:dup.extend([seen[key],vi])
   else:seen[key]=vi
  if dup:
   c.polyMergeVertex([ob+'.vtx[%d]'%v for v in sorted(set(dup))],distance=.0003,alwaysMergeTwoVertices=False,constructionHistory=False);weld_count+=len(dup)//2
 c.polyNormal(ob,normalMode=2,userNormalMode=0,constructionHistory=False)
 c.polySoftEdge(ob,angle=45,constructionHistory=False)
 c.delete(ob,constructionHistory=True);c.makeIdentity(ob,apply=True,translate=True,rotate=True,scale=True,normal=1)
 sel=om.MSelectionList();sel.add(ob);dag=sel.getDagPath(0);dag.extendToShape();fn=om.MFnMesh(dag)
 it=om.MItMeshEdge(dag);boundary=0;nonmanifold=0
 while not it.isDone():
  faces=it.getConnectedFaces();boundary+=len(faces)==1;nonmanifold+=len(faces)!=2;it.next()
 it=om.MItMeshPolygon(dag);zero=0
 while not it.isDone():zero+=it.getArea()<1e-8;it.next()
 nmverts=c.polyInfo(ob,nonManifoldVertices=True) or []
 assert boundary==0 and nonmanifold==0 and zero==0 and not nmverts,(name,boundary,nonmanifold,zero,nmverts)
 row={'mesh':name,'vertices':fn.numVertices,'faces':fn.numPolygons,'shells':len(shells),'single_face_shells':sum(len(s)==1 for s in shells),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'zero_area_faces':zero,'nonmanifold_vertices':len(nmverts),'welded_pairs':weld_count,'uv_count':fn.numUVs(),'role':d['role']};report.append(row)
 c.select(ob,replace=True);mel.eval('FBXResetExport;');mel.eval('FBXExportUpAxis z;');mel.eval('FBXExportSmoothingGroups -v true;');mel.eval('FBXExportTangents -v true;');mel.eval('FBXExportEmbeddedTextures -v false;');mel.eval('FBXExportCameras -v false;');mel.eval('FBXExportLights -v false;')
 mel.eval('FBXExport -f "%s" -s;'%(O/'Exports'/(name+'.fbx')).as_posix())
 c.parent(ob,ROOT);meshes.append(ob)
library=json.loads((O/'Source/library.json').read_text(encoding='utf8'))
for i,(name,rec) in enumerate(library['models'].items()):
 grp=c.group(rec['parts'],name=name+'_Assembly',parent=ROOT);c.setAttr(grp+'.translateX',(i%5)*360);c.setAttr(grp+'.translateY',-(i//5)*360)
c.file(rename=str(O/'Source/V55_Hotel_Furniture_Repaired.mb'));c.file(save=True,type='mayaBinary',force=True)
(O/'Audit/maya_topology.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('V55_MAYA_SUCCESS',len(report),sum(r['faces'] for r in report))
maya.standalone.uninitialize()
