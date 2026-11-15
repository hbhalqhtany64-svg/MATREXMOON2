# MATREXMOON
**NASA Space Apps Challenge 2026 – Orion Team (Tabuk) · Project: Matrix Moon · Challenge: Lunar Landing Site Navigator**

## Summary
An interactive web tool to compare lunar landing sites and time windows. Click any point on the Moon to see the nearest past mission, terrain elevation and slope (NASA LRO/LOLA), estimated power needs, illumination, shadow, temperature, Earth-communication status and dust level. A date/time selector moves the Sun across the surface (JPL Horizons data for 15 Nov 2026 – 15 Jan 2027). Near six reference points the data panel also shows a NASA QuickMap reading (local slope, elevation) as a cross-check.

## Run
    pip install -r requirements.txt
    python backend/app.py      # open http://localhost:5000
Without the server, open `index.html` directly (or host it on GitHub Pages): the interface falls back to local calculation.

## API
- `GET /api/missions`
- `GET /api/site?lat=-69.37&lon=32.32&sun=0`  (`sun` = sub-solar longitude, degrees). The response includes `quickmap` (NASA QuickMap reading) when a reference point is within 50 km, otherwise `null`.

## NASA data used
- **LRO LOLA LDEM_4** (elevation; slope derived) – https://imbrium.mit.edu/DATA/LOLA_GDR/CYLINDRICAL/IMG/ · rebuild: `python tools/build_terrain.py LDEM_4.IMG backend/terrain.json`
- **JPL Horizons (DE441)** – sub-solar longitude, 6-hour steps, 15 Nov 2026 – 15 Jan 2027: `data/horizons_results.txt`. The date selector interpolates these values; outside that window it uses an approximate 29.53-day cycle (offset 2.6° to match Horizons).
- **LRO QuickMap (LOLA DEM / GLD100 slope)** – readings at Apollo 11, Apollo 17, Chang'e 4, Chandrayaan-3 and two Shackleton-region points: `data/quickmap_reference.json`, report in `docs/QuickMap_LROC_report_AR.pdf`, LROC image `assets/quickmap-lroc-chandrayaan3.png` (Chandrayaan-3 area, 200 m/px, georeferenced by `docs/quickmap-lroc.vrt`).
- References: NASA Moon Trek, CSA Moon Exploration.
- Illumination, temperature, dust, communication and power values are approximate models, not NASA measurements. Slope is regional (1° grid, ~15 km baseline).

## Cross-check against NASA tools
`python tools/crosscheck.py` writes `data/crosscheck.json`.
- **Elevation vs QuickMap:** within 0.4 km at Apollo 11 (75 m), Chang'e 4 (357 m) and Chandrayaan-3 (−310 m); 1.2 km off at Apollo 17 and far off at the Shackleton rim, because a 1° cell (~30 km) averages the terrain.
- **Slope does not match:** our slope is regional (1° grid) while QuickMap's is local (200 m/px), e.g. Chandrayaan-3 1.2° vs 4.57°, Chang'e 4 4.7° vs 0.29°. Use QuickMap as the final check for any shortlisted site.
- **Sun vs JPL Horizons (245 samples):** the previous mean-cycle formula was off by 2.6° on average (max 4.0°). With the 2.6° offset it is 0.5° (max 1.4°) and inside the Horizons window the tool uses Horizons directly.
- The Shackleton floor point's coordinates are copied as written in the QuickMap report; please re-check them in QuickMap.

## Use of AI
Built with help from Claude (Anthropic) for code and text.

## Team
- Sarah Ali Al-Ghamdi – GitHub hosting and file upload
- Lamar Saad Al-Ahmari – Pitch deck, design and project materials
- Hebah Khalid Al-Qahtani – Tool website development

## Machine learning
`tools/train_suitability.py` trains a logistic regression on NASA LOLA elevation, slope, |latitude| and Earth line-of-sight. The 11 past soft-landing sites are the positives; the rest of the Moon is unlabeled background. The output is a **0–100 percentile of similarity to past landing sites** (data panel, map layer, ML panel and ML Lab).
- **Validation:** leave-one-site-out (hold one site out, rank it among all 64,800 cells). Mean percentile **76** (≈ AUC 0.76, random = 50), median 88.8. It works for near-side equatorial sites but **fails for the far side and poles** (Chang'e 4: 5th, Chandrayaan-3: 27th percentile). See `data/ml_report.json`.
- **Not** a safety or mission-success predictor: only 11 examples, selection bias, no failed-landing labels.
- **ML panel and ML Lab** (in `index.html`): score gauge, per-feature contribution bars, validation chart, model card, and a full-screen lab with a scan animation and per-feature contribution maps. The coefficients are hard-coded in the `MLM` constant; regenerate them with `python tools/export_ml_coefficients.py backend/terrain.json` if you retrain.

## Project layout
    index.html            frontend (works standalone, falls back to local calculation)
    backend/app.py        Flask API + SQLite   |  backend/terrain.json  LOLA 1° grid + ML scores
    tools/                build_terrain.py, train_suitability.py, export_ml_coefficients.py
    data/                 ml_report.json, LDEM_4.LBL
    assets/               put nasa-logo.png here (official, unmodified)
