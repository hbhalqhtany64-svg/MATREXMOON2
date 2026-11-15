"""Prints the logistic-regression coefficients used by the ML panel and ML Lab in index.html (MLM constant).
Usage: python tools/export_ml_coefficients.py backend/terrain.json"""
import base64, json, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
t = json.load(open(sys.argv[1]))
E = np.frombuffer(base64.b64decode(t["elev_b64"]), dtype='<i2').reshape(180, 360).astype(float)
S = np.frombuffer(base64.b64decode(t["slope_b64"]), dtype=np.uint8).reshape(180, 360) / 10.0
lat = 89.5 - np.arange(180)[:, None] * np.ones((1, 360)); lon = (np.arange(360)[None, :] + .5) * np.ones((180, 1))
cz = np.cos(np.radians(lat)) * np.cos(np.radians(lon))
X = np.stack([E.ravel() / 1000, S.ravel(), np.abs(lat).ravel() / 90, cz.ravel()], 1)
SITES = [(0.67,23.47),(-3.01,-23.42),(-3.65,-17.47),(26.13,3.63),(-8.97,15.5),(20.19,30.77),(7.08,-64.37),(44.12,-19.51),(-45.46,177.6),(-69.37,32.32),(-13.3,25.25)]
y = np.zeros(len(X)); y[[min(179, int(90 - a)) * 360 + int(b % 360) for a, b in SITES]] = 1
sc = StandardScaler().fit(X); m = LogisticRegression(class_weight='balanced', C=1.0, max_iter=1000).fit(sc.transform(X), y)
print("const MLM=" + json.dumps(dict(w=m.coef_[0].round(4).tolist(), mu=sc.mean_.round(4).tolist(), sd=sc.scale_.round(4).tolist())) + ";")
