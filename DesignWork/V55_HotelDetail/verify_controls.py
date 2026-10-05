import unreal as u,json,hashlib
from pathlib import Path
P=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()));O=P/'DesignWork/V55_HotelDetail'
AS=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
actors=list(AS.get_all_level_actors());controls=[]
for token in ['Sofa_Wood','EntryWardrobe_Wood','DoubleBed_Wood']:
 a=next(a for a in actors if a.get_actor_label().startswith('H55_307_') and a.get_actor_label().endswith(token))
 c,e=a.get_actor_bounds(False)
 r=u.SystemLibrary.capsule_trace_single(W,u.Vector(c.x,c.y,c.z+e.z+200),u.Vector(c.x,c.y,c.z-e.z-100),34,88,u.TraceTypeQuery.ECC_VISIBILITY,True,[x for x in actors if x!=a],u.DrawDebugTrace.NONE,True)
 controls.append({'actor':a.get_actor_label(),'collision_enabled':str(a.static_mesh_component.get_collision_enabled()),'profile':str(a.static_mesh_component.get_collision_profile_name()),'detected':r is not None})
data=json.loads((O/'Audit/live_collision.json').read_text(encoding='utf8'));data['positive_controls']=controls
data['paths_clear']=all(x['result']=='None' for x in data['traces']);data['floors_detected']=all(x['result']!='None' for x in data['floor_traces'])
data['protected_recheck']={}
for fn in ['protected_hashes_before.json','material_hashes_before.json']:
 for rel,h in json.loads((O/'Audit'/fn).read_text(encoding='utf8')).items():
  if not rel.endswith('Main_World2_MonitorArchitectural.umap'):
   data['protected_recheck'][rel]=hashlib.sha256((P/rel).read_bytes()).hexdigest()==h
(O/'Audit/live_collision.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
assert all(x['detected'] for x in controls),controls
assert data['paths_clear'] and data['floors_detected']
assert all(data['protected_recheck'].values())
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(19200,810,7460),u.Rotator(pitch=-18,yaw=48,roll=0))
u.AutomationLibrary.take_high_res_screenshot(1600,1000,str(O/'Preview/UE_307_Overview.png'))
u.log('V55_POSITIVE_CONTROLS_PASSED')
