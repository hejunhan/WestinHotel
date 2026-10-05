import unreal as u,json,hashlib,math,datetime,traceback
from pathlib import Path
P=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()));O=P/'DesignWork/V55_HotelDetail'
EXPECTED='/Game/DSH_交互/V44_建筑制图监控/Maps/Main_World2_MonitorArchitectural.Main_World2_MonitorArchitectural';LV=EXPECTED+':PersistentLevel';DST='/Game/DSH_HotelDetail/V55_Furniture'
assert str(P).replace('\\','/').rstrip('/')=='C:/Users/Lenovo/WestinHotel'
AS=u.get_editor_subsystem(u.EditorActorSubsystem);ES=u.get_editor_subsystem(u.UnrealEditorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem);w=ES.get_editor_world()
assert w.get_path_name()==EXPECTED and LS.get_current_level().get_path_name()==LV
baseline=json.loads((O/'Audit/protected_hashes_before.json').read_text());matbase=json.loads((O/'Audit/material_hashes_before.json').read_text());allhash={**baseline,**matbase}
for name,h in allhash.items():
 if name.endswith('Main_World2_MonitorArchitectural.umap'):continue
 assert hashlib.sha256((P/name).read_bytes()).hexdigest()==h,'Protected file changed before apply: '+name
assert not any(a.get_actor_label().startswith('H55_307_') for a in AS.get_all_level_actors()),'Room already applied; do not duplicate'
hotel=next(a for a in AS.get_all_level_actors() if a.get_actor_label()=='dongshuhe_F3' and a.get_level().get_path_name()==LV)
old=hotel.static_mesh_component.static_mesh;beforebox=hotel.get_actor_bounds(False)
old_info={'actor':hotel.get_path_name(),'original_mesh':old.get_path_name(),'transform':str(hotel.get_actor_transform()),'bounds':[list(v.to_tuple()) for v in beforebox]}
name='SM_H55_HotelShell307'
if not u.EditorAssetLibrary.does_asset_exist(DST+'/'+name):
 opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.import_animations=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.automated_import_should_detect_type=False
 si=opts.static_mesh_import_data;si.combine_meshes=True;si.auto_generate_collision=False;si.generate_lightmap_u_vs=False;si.remove_degenerates=True;si.convert_scene=True;si.convert_scene_unit=True;si.force_front_x_axis=False
 t=u.AssetImportTask();t.filename=str(O/'Exports'/(name+'.fbx'));t.destination_path=DST;t.destination_name=name;t.automated=True;t.replace_existing=False;t.save=False;t.options=opts;t.factory=u.FbxFactory();u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
new=u.load_asset(DST+'/'+name);assert isinstance(new,u.StaticMesh)
ob,nb=old.get_bounds(),new.get_bounds()
assert max(abs(a-b) for a,b in zip(ob.origin.to_tuple(),nb.origin.to_tuple()))<.1,(ob,nb)
assert max(abs(a-b) for a,b in zip(ob.box_extent.to_tuple(),nb.box_extent.to_tuple()))<.1,(ob,nb)
new.set_material(0,hotel.static_mesh_component.get_material(0));bs=new.get_editor_property('body_setup');bs.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
u.EditorAssetLibrary.save_loaded_asset(new,only_if_is_dirty=False)
L=json.loads((O/'Source/library.json').read_text(encoding='utf8'));created=[]
with u.ScopedEditorTransaction('V55 furnish hotel 307 in Persistent Level only'):
 hotel.modify();hotel.static_mesh_component.set_static_mesh(new)
 for it in L['placements']:
  x=L['origin_ue_cm'][0]+(it['x']+it['w']/2)*100;y=L['origin_ue_cm'][1]+(it['y']+it['d']/2)*100;z=L['origin_ue_cm'][2]
  for pn in L['models'][it['model']]['parts']:
   assert LS.get_current_level().get_path_name()==LV
   sm=u.load_asset(DST+'/'+pn);assert isinstance(sm,u.StaticMesh)
   a=AS.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,z),u.Rotator(pitch=0,yaw=it['yaw'],roll=0));assert a.get_level().get_path_name()==LV
   a.set_actor_label('H55_307_'+it['id']+'_'+pn.removeprefix('H55_'));a.set_folder_path('DSH_HotelDetail/V55/307_Furniture');a.tags=['H55_Hotel307','H55_Item='+it['id'],'H55_Role='+pn.rsplit('_',1)[1]];a.static_mesh_component.set_static_mesh(sm);a.static_mesh_component.set_mobility(u.ComponentMobility.STATIC);created.append(a)
 group=u.ActorGroupingUtils.get().group_actors(created);assert group and group.get_level().get_path_name()==LV
 group.set_actor_label('GROUP_H55_307_HotelFurniture');group.set_folder_path('DSH_HotelDetail/V55');group.tags=['H55_Hotel307_Group']
afterbox=hotel.get_actor_bounds(False)
assert max(abs(a-b) for va,vb in zip(beforebox,afterbox) for a,b in zip(va.to_tuple(),vb.to_tuple()))<.1
report={'time':datetime.datetime.now().isoformat(),'project':str(P),'level':LV,'hotel':old_info,'replacement_mesh':new.get_path_name(),'group':group.get_path_name(),'actors':[],'only_persistent_saved':False}
for a in created:
 b,e=a.get_actor_bounds(False);report['actors'].append({'label':a.get_actor_label(),'path':a.get_path_name(),'level':a.get_level().get_path_name(),'center':list(b.to_tuple()),'extent':list(e.to_tuple()),'mesh':a.static_mesh_component.static_mesh.get_path_name()})
(O/'Audit/applied_scene.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
assert all(a.get_level().get_path_name()==LV for a in created)
assert LS.get_current_level().get_path_name()==LV
report['only_persistent_saved']=bool(LS.save_current_level())
assert report['only_persistent_saved']
report['protected_files_unchanged']={name:hashlib.sha256((P/name).read_bytes()).hexdigest()==h for name,h in allhash.items() if not name.endswith('Main_World2_MonitorArchitectural.umap')}
assert all(report['protected_files_unchanged'].values())
(O/'Audit/applied_scene.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(19760,825,7248),u.Rotator(pitch=-8,yaw=95,roll=0))
AS.set_selected_level_actors([])
u.log('V55_ROOM_APPLIED '+str(len(created))+' meshes; protected files unchanged')
