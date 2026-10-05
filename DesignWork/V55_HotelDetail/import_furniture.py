import unreal as u,json,datetime,hashlib
from pathlib import Path
P=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()));O=P/'DesignWork/V55_HotelDetail'
EXPECTED='/Game/DSH_交互/V44_建筑制图监控/Maps/Main_World2_MonitorArchitectural.Main_World2_MonitorArchitectural'
assert str(P).replace('\\','/').rstrip('/')=='C:/Users/Lenovo/WestinHotel'
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();assert w.get_path_name()==EXPECTED
assert u.get_editor_subsystem(u.LevelEditorSubsystem).get_current_level().get_path_name()==EXPECTED+':PersistentLevel'
DST='/Game/DSH_HotelDetail/V55_Furniture';u.EditorAssetLibrary.make_directory(DST)
library=json.loads((O/'Source/library.json').read_text(encoding='utf8'))
matpaths={'Wood':'/Game/Mat/MI_Wood1','Metal':'/Game/DSH_交互/V43_实时俯视监控/Materials/M_M43_CharcoalMetal','Fabric':'/Game/Materials_Frabric/Materials/MI_Fabric_valvet_01','Stone':'/Game/Mat/MI_Concrete1','Default':'/Engine/EngineMaterials/DefaultMaterial'}
mats={};hashes={}
for role,path in matpaths.items():
 mats[role]=u.load_asset(path) or u.load_asset('/Engine/EngineMaterials/DefaultMaterial')
 if path.startswith('/Game/'):
  f=P/'Content'/(path[6:]+'.uasset')
  if f.exists():hashes[str(f.relative_to(P))]=hashlib.sha256(f.read_bytes()).hexdigest()
(O/'Audit/material_hashes_before.json').write_text(json.dumps(hashes,indent=2))
tasks=[]
for rec in library['models'].values():
 for name in rec['parts']:
  if u.EditorAssetLibrary.does_asset_exist(DST+'/'+name):continue
  opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.import_animations=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.automated_import_should_detect_type=False
  si=opts.static_mesh_import_data;si.combine_meshes=True;si.auto_generate_collision=True;si.generate_lightmap_u_vs=True;si.remove_degenerates=True;si.convert_scene=True;si.convert_scene_unit=True;si.force_front_x_axis=False
  task=u.AssetImportTask();task.filename=str(O/'Exports'/(name+'.fbx'));task.destination_path=DST;task.destination_name=name;task.automated=True;task.replace_existing=False;task.save=False;task.options=opts;task.factory=u.FbxFactory();tasks.append(task)
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
report=[]
for rec in library['models'].values():
 for name in rec['parts']:
  sm=u.load_asset(DST+'/'+name);assert isinstance(sm,u.StaticMesh),name
  role=name.rsplit('_',1)[1]
  for i in range(len(sm.get_editor_property('static_materials'))):sm.set_material(i,mats[role])
  bs=sm.get_editor_property('body_setup');bs.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
  sm.set_editor_property('light_map_resolution',128)
  u.EditorAssetLibrary.save_loaded_asset(sm,only_if_is_dirty=False)
  b=sm.get_bounds()
  report.append({'name':name,'asset':sm.get_path_name(),'material':mats[role].get_path_name(),'center':list(b.origin.to_tuple()),'extent':list(b.box_extent.to_tuple()),'vertices':u.EditorStaticMeshLibrary.get_number_verts(sm,0)})
(O/'Audit/ue_import.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
u.log('V55_IMPORT_SUCCESS '+str(len(report)))
