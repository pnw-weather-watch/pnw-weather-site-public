import json,numpy as np,sys
sys.argv=['x']; exec(open('local/nudge2.py').read().split('C0=')[0].replace("local/temp_scale_before_nudge.json","theme/temp_scale.json"))
P=0
TS=json.load(open('theme/temp_scale.json')); te=TS['edges_F']; tc=TS['colors']
C=np.array([h2r(c) for c in tc]); mid=np.array([te[0]-1]+[(te[i-1]+te[i])/2 for i in range(1,len(te))]+[te[-1]+1])
a,b=-40.0,33.0
new=C.copy()
K=0.22
for i,t in enumerate(mid):
    if -12<t<32:
        w=np.sin(np.pi*(t+12)/44)**1.2   # 0 at -12F and 32F, peak near 10F
        w*= 1 if t<=10 else 1
        new[i]=C[i]*(1-K*w); new[i,2]=C[i,2]*(1-0.25*K*w)
def dE(X):
    o=[]
    for M in SIM: L=lab(X@M.T); o.append(np.linalg.norm(L[1:]-L[:-1],axis=1))
    return np.minimum(*o)
inner=new[1:-1]; d=dE(np.round(inner)); print('min',d.min().round(2),'at',te[int(d.argmin())])
for i,t in enumerate(mid):
    if -14<t<36: print(t, tc[i], r2h(new[i]))
json.dump(dict(TS,colors=[r2h(c) for c in new],note_blues="11-04 5:52 PM Benjamin: blues darken sooner (-12..32F remapped, exponent 1.55); warm side unchanged"),open('local/temp_scale_blues.json','w'),indent=0)
from scipy.optimize import minimize
idx=[i for i,t in enumerate(mid) if -16<t<33]; base=new.copy()
def full(x): X=base.copy(); X[idx]=x.reshape(-1,3); return X[1:-1]
def both(X):
    o=[]
    for M in SIM: L=lab(X@M.T); o.append(np.linalg.norm(L[1:]-L[:-1],axis=1))
    return np.concatenate(o)
x0=base[idx].ravel()
np_=len(base)-3; pm=np.array([(k+1 in idx) or (k+2 in idx) for k in range(np_)]); MASK=np.concatenate([pm,pm])
print('pre-existing min outside window',both(np.round(base[1:-1]))[~MASK].min().round(2))
r=minimize(lambda x:np.sum((x-x0)**2)/1e3,x0,method='SLSQP',constraints=[{'type':'ineq','fun':lambda x:both(full(x))[MASK]-3.5}],bounds=[(0,255)]*len(x0),options={'maxiter':3000})
new[idx]=r.x.reshape(-1,3); d=both(np.round(new[1:-1])); print(r.message,'final min',d.min().round(2))
for i in idx: print(mid[i], tc[i], r2h(new[i]))
json.dump(dict(TS,colors=[r2h(c) for c in new],note_blues="11-04 5:52 PM Benjamin: blues darken sooner (-12..32F remapped toward colder colors), then minimal CVD fix (deutan/protan dE>=3); warm side unchanged"),open('local/temp_scale_blues.json','w'),indent=0)
