import json,numpy as np
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
O=Path('C:/Users/Lenovo/WestinHotel/DesignWork/V55_HotelDetail')
D=np.load(O/'Audit/f3_raw.npz'); v=D['vertices'];t=D['triangles']
# FBX export flips the Unreal local Y axis. Current actor rolls -90 about X.
w=np.stack([v[:,0]*100+14615.131025,v[:,2]*100+457.395898,v[:,1]*100+4766.847454],axis=1)
np.savez_compressed(O/'Audit/f3_world.npz',vertices=w,triangles=t)
print('world',w.min(0),w.max(0))
zvals,count=np.unique(np.round(w[:,2],1),return_counts=True); print('Z modes',sorted(zip(zvals.tolist(),count.tolist()),key=lambda p:-p[1])[:35])
minx,miny,minz=w.min(0); scale=.25
im=Image.new('RGB',(1400,1370),'#efede5');dr=ImageDraw.Draw(im)
def p(a):return (50+(a[0]-minx)*scale,50+(a[1]-miny)*scale)
for tri in t[np.argsort(w[t,2].mean(1))]:
 pts=w[tri]
 if pts[:,2].min()<7010:continue
 if abs(np.cross(pts[1]-pts[0],pts[2]-pts[0])[2])<5:
  if pts[:,2].min()<7240 and pts[:,2].max()>7240:
   dr.line([p(a) for a in pts]+[p(pts[0])],fill='#374b4b',width=2)
  continue
 if pts[:,2].max()>7350:continue
 h=pts[:,2].mean();col='#c9c6bc' if h<7110 else '#7f8581' if h<7250 else '#374b4b'
 dr.polygon([p(a) for a in pts],fill=col)
for x in range(0,5101,500):
 dr.line([(50+x*scale,50),(50+x*scale,1280)],fill='#ada99c',width=1);dr.text((50+x*scale,20),str(x/100),fill='black')
for y in range(0,4861,500):
 dr.line([(50,50+y*scale),(1325,50+y*scale)],fill='#ada99c',width=1);dr.text((5,50+y*scale),str(y/100),fill='black')
dr.rectangle([p((19027,1129)),p((19109,1409))],outline='red',width=4)
im.save(O/'Preview/Hotel_existing_plan.png')
parts=json.loads((O/'Audit/components_raw.json').read_text()); comps=[]
for i,c in enumerate(parts):
 lo,hi=c['min'],c['max'];c['id']=i;c['wmin']=[lo[0]*100+14615.131025,lo[2]*100+457.395898,lo[1]*100+4766.847454];c['wmax']=[hi[0]*100+14615.131025,hi[2]*100+457.395898,hi[1]*100+4766.847454];comps.append(c)
(O/'Audit/components_world.json').write_text(json.dumps(comps,indent=2))
print('room components')
for c in comps:
 lo,hi=np.array(c['wmin']),np.array(c['wmax'])
 if lo[0]>19000 and hi[0]<20200 and lo[1]>700 and hi[1]<2890:
  print(c['id'],np.round(lo,1),np.round(hi-lo,1),c['faces'])
