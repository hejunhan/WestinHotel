import os,json
from pathlib import Path
O=Path('C:/Users/Lenovo/WestinHotel/DesignWork/V55_HotelDetail')
os.environ['MAYA_APP_DIR']=str(O/'Source/MayaSession');os.environ['MAYA_DISABLE_CIP']='1'
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as c,maya.api.OpenMaya as om,maya.mel as mel
c.file(new=True,force=True);c.currentUnit(linear='cm');c.upAxis(axis='z',rotateView=True);c.loadPlugin('fbxmaya',quiet=True)
d=json.loads((O/'Source/Shell307_candidate.json').read_text());pts=om.MPointArray([om.MPoint(v[0],-v[1],v[2]) for v in d['vertices_cm']]);counts=[len(f) for f in d['faces']];ids=[v for f in d['faces'] for v in reversed(f)]
fn=om.MFnMesh();fn.create(pts,counts,ids);ob=c.listRelatives(fn.fullPathName(),parent=True,fullPath=True)[0];ob=c.rename(ob,d['name']);sel=om.MSelectionList();sel.add(ob);dag=sel.getDagPath(0);dag.extendToShape();fn=om.MFnMesh(dag)
uv=[p for f in d['uvs'] for p in reversed(f)];fn.setUVs([p[0] for p in uv],[p[1] for p in uv]);fn.assignUVs(counts,list(range(len(uv))));c.sets(ob,edit=True,forceElement='initialShadingGroup');c.polySoftEdge(ob,angle=30,constructionHistory=False);c.delete(ob,constructionHistory=True)
c.select(ob,replace=True);mel.eval('FBXResetExport;');mel.eval('FBXExportUpAxis z;');mel.eval('FBXExportSmoothingGroups -v true;');mel.eval('FBXExportEmbeddedTextures -v false;');mel.eval('FBXExport -f "%s" -s;'%(O/'Exports/SM_H55_HotelShell307.fbx').as_posix())
c.file(rename=str(O/'Source/V55_HotelShell307_Independent.mb'));c.file(save=True,type='mayaBinary',force=True)
print('SHELL_EXPORTED',fn.numVertices,fn.numPolygons);maya.standalone.uninitialize()
