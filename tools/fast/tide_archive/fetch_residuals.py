#!/usr/bin/env python3
#!/usr/bin/env python3
"""Monthly tide residual (hourly_height - hourly prediction) per station, for the SST k fit. Usage: fetch_residuals.py HIRES_DIR [ids]"""
import json, os, time, urllib.request, datetime as D
UA={"User-Agent":"pnw-weather-tides"}
API="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?application=pnw_weather_tides&time_zone=gmt&units=english&format=json&datum=MLLW"
ST=["9439040","9440910","9441102","9442396","9443090","9444090","9444900","9449880","9449424","9447130","9446484"]
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tide_stations_ca as _CA
ST = ST + list(_CA.CA)
if len(sys.argv) > 2: ST = sys.argv[2].split(",")
OUT = (sys.argv[1] if len(sys.argv) > 1 else "/tmp/sst_work/hires") + "/residuals"
os.makedirs(OUT, exist_ok=True)

def get(url, retries=5):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url, headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=120).read())
        except Exception as e:
            last=e; time.sleep(2+i*2)
    raise last

def series(prod, st, b, e, extra=""):
    u=f"{API}&product={prod}&station={st}&begin_date={b}&end_date={e}{extra}"
    j=get(u)
    out={}
    for p in (j.get("predictions") or j.get("data") or []):
        v=p.get("v")
        if v in ("", None): continue
        try: out[p["t"]]=float(v)
        except: pass
    return out

chunks=[
 ("20230601","20240531"),("20240601","20250531"),("20250601","20260531"),("20260601","20261115")
]
for st in ST:
    dest=os.path.join(OUT,f"{st}.json")
    cur=json.load(open(dest)) if os.path.exists(dest) else {"station":st,"obs":{},"pred":{}}
    for b,e in chunks:
        nobs=sum(1 for t in cur["obs"] if b[:4]<=t[:4]<=e[:4])
        if nobs>8000 and sum(1 for t in cur["pred"] if b[:4]<=t[:4]<=e[:4])>8000:
            continue
        print(st,b,e,"...",flush=True)
        try:
            obs=series("hourly_height",st,b,e)
            pred=series("predictions",st,b,e,"&interval=h")
        except Exception as ex:
            print(" FAIL",ex,flush=True); continue
        cur["obs"].update(obs); cur["pred"].update(pred)
        json.dump(cur, open(dest,"w"))
        print("  obs",len(obs),"pred",len(pred),"tot",len(cur["obs"]),len(cur["pred"]),flush=True)
    # residual daily / monthly
    res={}
    for t,o in cur["obs"].items():
        p=cur["pred"].get(t)
        if p is not None:
            res[t]=o-p
    cur["resid_hourly"]=res
    mon={}
    for t,v in res.items():
        mon.setdefault(t[:7],[]).append(v)
    cur["resid_monthly"]={m:round(sum(vs)/len(vs),4) for m,vs in mon.items() if len(vs)>=200}
    json.dump(cur, open(dest,"w"))
    print(st,"monthly",sorted(cur["resid_monthly"]),flush=True)
print("done")
