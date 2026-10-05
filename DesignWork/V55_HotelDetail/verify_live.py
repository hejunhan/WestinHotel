import unreal as u,json,traceback
from pathlib import Path
O=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))/'DesignWork/V55_HotelDetail'
AS=u.get_editor_subsystem(u.EditorActorSubsystem);w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();D=json.loads((O/'Audit/layout_validation.json').read_text(encoding='utf8'));origin=D['room_origin_ue_cm'];report={'capsule_radius_cm':34,'capsule_halfheight_cm':88,'traces':[],'floor_traces':[],'docs':{'capsule':u.SystemLibrary.capsule_trace_single.__doc__,'line':u.SystemLibrary.line_trace_single.__doc__}}
def vec(p,z=90):return u.Vector(origin[0]+p[0]*100,origin[1]+p[1]*100,origin[2]+z)
for name,path in D['paths'].items():
 for a,b in zip(path,path[1:]):
  r=u.SystemLibrary.capsule_trace_single(w,vec(a),vec(b),34,88,u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],u.DrawDebugTrace.NONE,True)
  report['traces'].append({'route':name,'start':a,'end':b,'result':str(r)})
 p=path[-1];r=u.SystemLibrary.line_trace_single(w,vec(p,100),vec(p,-20),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],u.DrawDebugTrace.NONE,True)
 report['floor_traces'].append({'name':name,'result':str(r)})
report['dirty_maps']=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
(O/'Audit/live_collision.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(19760,825,7248),u.Rotator(pitch=-8,yaw=95,roll=0))
u.AutomationLibrary.take_high_res_screenshot(1600,1000,str(O/'Preview/UE_307_Entry.png'))
u.log('V55_LIVE_COLLISION_COMPLETE '+str(len(report['traces'])))
