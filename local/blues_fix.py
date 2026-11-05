import json,numpy as np
from scipy.optimize import minimize
src=open('qa/guard.py').read(); a=src.index('def lin'); b=src.index('async def main'); g={}; exec("import io\n"+src[a:b],g)
TS=json.load(open('theme/temp_scale.json')); tc=TS['colors']; te=TS['edges_F']
h2r=lambda h:[int(h.lstrip('#')[i:i+2],16) for i in (0,2,4)]; r2h=lambda c:'#%02x%02x%02x'%tuple(int(max(0,min(255,round(x)))) for x in c)
C=np.array([h2r(c) for c in tc],float); mid=[te[0]-1]+[(te[i-1]+te[i])/2 for i in range(1,len(te))]+[te[-1]+1]
idx=[i for i,t in enumerate(mid) if -16<t<32]; x0=C[idx].ravel()
def sims(X):
    o=[]
    for M in g['SIM'].values():
        L=np.array([g['lab'](tuple(sum(M[i][j]*p[j] for j in range(3)) for i in range(3))) for p in X]); o.append(L)
    return o
lo,hi=idx[0]-2,idx[-1]+3
def cons(x):
    X=C.copy(); X[idx]=x.reshape(-1,3); out=[]
    for L in sims(X[lo:hi]):
        for s in (1,2): out+=list(np.linalg.norm(L[s:]-L[:-s],axis=1)-3.6)
    return np.array(out)
r=minimize(lambda x:np.sum((x-x0)**2)/1e3,x0,method='SLSQP',constraints=[{'type':'ineq','fun':cons}],bounds=[(0,255)]*len(x0),options={'maxiter':300})
print(r.message, cons(np.round(r.x)).min()+3.6)
C[idx]=r.x.reshape(-1,3)
for i in idx: print(mid[i],tc[i],r2h(C[i]))
TS['colors']=[r2h(c) for c in C]; json.dump(TS,open('theme/temp_scale.json','w'),indent=0)
