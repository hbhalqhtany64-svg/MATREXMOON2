"""Cross-check the tool against NASA reference data.
1) Elevation / slope at 6 points: our 1-degree LOLA grid vs NASA LRO QuickMap readings (data/quickmap_reference.json)
2) Sub-solar longitude: old mean-cycle formula (with and without the 2.6 deg offset) vs JPL Horizons (data/horizons_results.txt)
Run:  python tools/crosscheck.py   (writes data/crosscheck.json)"""
import base64, datetime as dt, json, os, re, statistics as st, struct
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
T = json.load(open(os.path.join(ROOT, "backend", "terrain.json")))
E = struct.unpack("<64800h", base64.b64decode(T["elev_b64"])); S = base64.b64decode(T["slope_b64"])
def lola(la, lo):
    i = min(179, int(90 - la)) * 360 + int(lo % 360); return E[i], S[i] / 10

out = {"sites": [], "sun": {}}
for q in json.load(open(os.path.join(ROOT, "data", "quickmap_reference.json")))["sites"]:
    e, s = lola(q["lat"], q["lon"])
    out["sites"].append(dict(name=q["name"], quickmap_elev_m=q["elevation_m"], grid_elev_m=e,
        elev_diff_m=None if q["elevation_m"] is None else round(e - q["elevation_m"]),
        quickmap_local_slope_deg=q["slope_deg"], grid_regional_slope_deg=round(s, 1)))

rows = []
for line in open(os.path.join(ROOT, "data", "horizons_results.txt")):
    m = re.match(r"\s*(\d{4})-(\w{3})-(\d\d) (\d\d):(\d\d), , , *([\d.-]+), *([\d.-]+), *([\d.-]+), *([\d.-]+),", line)
    if m:
        t = dt.datetime.strptime(f"{m[1]}-{m[2]}-{m[3]} {m[4]}:{m[5]}", "%Y-%b-%d %H:%M").replace(tzinfo=dt.timezone.utc)
        rows.append((t, float(m[8])))
ep = dt.datetime(2000, 1, 6, 18, 14, tzinfo=dt.timezone.utc)
def formula(t, off):
    fr = (((t - ep).total_seconds() / 86400 / 29.530588) % 1 + 1) % 1
    return 180 - 360 * fr - off
for off in (0, 2.6):
    errs = [((round(formula(t, off)) - (l if l <= 180 else l - 360)) + 180) % 360 - 180 for t, l in rows]
    out["sun"][f"offset_{off}"] = dict(samples=len(errs), mean_abs_deg=round(st.mean(abs(e) for e in errs), 2), max_abs_deg=round(max(abs(e) for e in errs), 2))
json.dump(out, open(os.path.join(ROOT, "data", "crosscheck.json"), "w"), indent=1)
for s in out["sites"]: print(s)
print(out["sun"])
