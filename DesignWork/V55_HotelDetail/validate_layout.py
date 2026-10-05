import json,math,numpy as np
from pathlib import Path
from collections import deque
from PIL import Image,ImageDraw
O=Path('C:/Users/Lenovo/WestinHotel/DesignWork/V55_HotelDetail');L=json.loads((O/'Source/library.json').read_text(encoding='utf8'));I={r['name']:r for r in json.loads((O/'Audit/ue_import.json').read_text(encoding='utf8'))}
boxes=[]
for p in L['placements']:
 pts=[];angle=math.radians(p['yaw']);cs,sn=math.cos(angle),math.sin(angle)
 for name in L['models'][p['model']]['parts']:
  imp=I[name];d=json.loads((O/'Source'/(name+'.json')).read_text());vs=np.array(d['vertices_cm']);lo=vs.min(0);hi=vs.max(0)
  assert np.max(np.abs(np.array(imp['center'])-(lo+hi)/2))<.01,(name,'center mismatch')
  assert np.max(np.abs(np.array(imp['extent'])-(hi-lo)/2))<.01,(name,'size mismatch')
  for x in [lo[0]/100,hi[0]/100]:
   for y in [lo[1]/100,hi[1]/100]:pts.append([p['x']+p['w']/2+x*cs-y*sn,p['y']+p['d']/2+x*sn+y*cs])
 q=np.array(pts);boxes.append({'id':p['id'],'name':p['name'],'min':q.min(0).tolist(),'max':q.max(0).tolist()})
overlaps=[]
for i,a in enumerate(boxes):
 for b in boxes[i+1:]:
  v=np.minimum(a['max'],b['max'])-np.maximum(a['min'],b['min'])
  if min(v)>.005:overlaps.append([a['id'],b['id'],v.tolist()])
# Cabinet movement envelope from actual current object; displaced along +worldY 3.8m.
sweep=[.0511,4.37155,.8711,10.97156]
sweephits=[]
for a in boxes:
 v=np.minimum(a['max'],sweep[2:])-np.maximum(a['min'],sweep[:2])
 if min(v)>.005:sweephits.append(a['id'])
# Existing room fixture volumes, preserved from actual mesh, plus bath partition.
existing=[[10.571,6.6,11.221,8.5],[8.871,11.85,9.121,13.25],[9.171,13.1,9.971,13.55],[10.571,11.75,11.171,12.4],[10.271,12.65,11.171,13.55]]
existinghits=[]
for a in boxes:
 for b in existing:
  ov=np.minimum(a['max'],b[2:])-np.maximum(a['min'],b[:2])
  if min(ov)>.005:existinghits.append([a['id'],b])
STEP=.05;R=.34;nx=int(11.2711553/STEP)+1;ny=int(13.65/STEP)+1
def grid(closed):
 g=np.ones((ny,nx),dtype=bool)
 obs=[[*a['min'],*a['max']] for a in boxes]+existing+[sweep if not closed else [.0511,4.37155,.8711,7.17156]]
 for iy in range(ny):
  y=iy*STEP
  for ix in range(nx):
   x=ix*STEP
   if x<R or x>11.2711553-R or y<R or y>13.65-R:g[iy,ix]=False;continue
   for a,b,c,d in obs:
    dx=max(a-x,0,x-c);dy=max(b-y,0,y-d)
    if dx*dx+dy*dy<R*R:g[iy,ix]=False;break
 return g
points={'entry':[7.37,.6],'task_book':[10.19,6.48],'wardrobe_front':[1.6,6.0],'bedside':[7.95,11.1],'bath_entrance':[8.35,12.1]}
def flood(g,start):
 a=(round(start[1]/STEP),round(start[0]/STEP));seen={a};q=deque([a]);parent={a:None}
 while q:
  y,x=q.popleft()
  for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
   if 0<=yy<ny and 0<=xx<nx and g[yy,xx] and (yy,xx) not in seen:seen.add((yy,xx));q.append((yy,xx));parent[(yy,xx)]=(y,x)
 return seen,parent
routes={};paths={}
for closed in [True,False]:
 g=grid(closed);seen,parent=flood(g,points['entry']);routes['wardrobe_closed' if closed else 'full_movement_envelope_reserved']={n:(round(p[1]/STEP),round(p[0]/STEP)) in seen for n,p in points.items()}
 if closed:
  for n,p in points.items():
   node=(round(p[1]/STEP),round(p[0]/STEP));seq=[]
   while node is not None and node in parent:seq.append(node);node=parent[node]
   seq.reverse();compact=[seq[0]]
   for i in range(1,len(seq)-1):
    if (seq[i][0]-seq[i-1][0],seq[i][1]-seq[i-1][1])!=(seq[i+1][0]-seq[i][0],seq[i+1][1]-seq[i][1]):compact.append(seq[i])
   if len(seq)>1:compact.append(seq[-1])
   paths[n]=[[x*STEP,y*STEP] for y,x in compact]
result={'scope':'actual UE imported dimensions plus 2D radius 34cm capsule footprint; does not prove runtime blueprint behavior or third-person camera','new_furniture_overlap':overlaps,'wardrobe_sweep_hits':sweephits,'retained_fixture_overlap':existinghits,'walk_routes':routes,'paths':paths,'boxes':boxes,'room_origin_ue_cm':L['origin_ue_cm']}
(O/'Audit/layout_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='boxes'},ensure_ascii=False,indent=2))
assert not overlaps and not sweephits and not existinghits
assert all(all(v.values()) for v in routes.values())
