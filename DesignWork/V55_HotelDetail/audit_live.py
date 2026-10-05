import unreal as u, json, datetime, traceback, hashlib, shutil
from pathlib import Path
P=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
O=P/'DesignWork/V55_HotelDetail'
for s in ['Audit','Source','Exports','Preview','Backup']: (O/s).mkdir(parents=True,exist_ok=True)
AS=u.get_editor_subsystem(u.EditorActorSubsystem)
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
EXPECTED='/Game/DSH_交互/V44_建筑制图监控/Maps/Main_World2_MonitorArchitectural.Main_World2_MonitorArchitectural'
assert str(P).replace('\\','/').rstrip('/')=='C:/Users/Lenovo/WestinHotel'
assert w.get_path_name()==EXPECTED
assert u.get_editor_subsystem(u.LevelEditorSubsystem).get_current_level().get_path_name()==EXPECTED+':PersistentLevel'
def pn(x):return x.get_path_name() if x else None
def v(x):return list(x.to_tuple())
D={'project':str(P),'world':pn(w),'time':datetime.datetime.now().isoformat(),'actors':[],'exports':[],'errors':[], 'dirty_maps':[pn(x) for x in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()]}
for a in AS.get_all_level_actors():
 try:
  b,e=a.get_actor_bounds(False)
  d={'label':a.get_actor_label(),'path':pn(a),'level':pn(a.get_level()),'class':a.get_class().get_name(),'parent':pn(a.get_attach_parent_actor()),'location':v(a.get_actor_location()),'rotation':v(a.get_actor_rotation()),'scale':v(a.get_actor_scale3d()),'bounds_center':v(b),'bounds_extent':v(e),'folder':str(a.get_folder_path()),'tags':[str(t) for t in a.tags],'meshes':[]}
  for c in a.get_components_by_class(u.StaticMeshComponent):
   sm=c.static_mesh
   if not sm:continue
   t=c.get_world_transform(); lo,hi=c.get_local_bounds()
   d['meshes'].append({'mesh':pn(sm),'component':pn(c),'location':v(t.translation),'quat':v(t.rotation),'scale':v(t.scale3d),'local_min':v(lo),'local_max':v(hi),'materials':[pn(c.get_material(i)) for i in range(c.get_num_materials())],'collision':str(c.get_collision_enabled()),'visible':c.is_visible()})
  D['actors'].append(d)
 except: D['errors'].append(traceback.format_exc())
assert len([a for a in D['actors'] if a['label']=='dongshuhe_F3' and a['level']==EXPECTED+':PersistentLevel'])==1
for name in ['dongshuhe_F3','guizi','MON_PlanCutaway_Hotel']:
 a=next((a for a in AS.get_all_level_actors() if a.get_actor_label()==name and pn(a.get_level())==EXPECTED+':PersistentLevel'),None)
 if not a or not isinstance(a,u.StaticMeshActor):continue
 task=u.AssetExportTask();task.object=a.static_mesh_component.static_mesh;task.filename=str(O/'Audit'/(name+'.fbx'));task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=u.StaticMeshExporterFBX()
 opt=u.FbxExportOption();opt.collision=False;opt.level_of_detail=False;task.options=opt
 D['exports'].append({'name':name,'ok':u.Exporter.run_asset_export_task(task),'errors':list(task.errors)})
(O/'Audit/live_before.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')
files=list((P/'Content/Level').glob('*.umap'))+[P/'Content/DSH_交互/V44_建筑制图监控/Maps/Main_World2_MonitorArchitectural.umap']
for d in D['actors']:
 if d['label'] in ['dongshuhe_F3','guizi']:
  for c in d['meshes']:
   files.append(P/'Content'/(c['mesh'].split('.')[0].removeprefix('/Game/')+'.uasset'))
H={str(f.relative_to(P)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in set(files) if f.exists()}
(O/'Audit/protected_hashes_before.json').write_text(json.dumps(H,indent=2),encoding='utf8')
src=P/'Content/DSH_交互/V44_建筑制图监控/Maps/Main_World2_MonitorArchitectural.umap'
if not (O/'Backup/Main_World2_before_V55.umap').exists():shutil.copy2(src,O/'Backup/Main_World2_before_V55.umap')
u.log('V55_AUDIT_COMPLETE '+json.dumps({'actors':len(D['actors']),'exports':D['exports'],'errors':D['errors']},ensure_ascii=False))
