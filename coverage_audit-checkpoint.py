"""
HIRDS coverage audit and design-storm index.

Input : hirds.csv (HIRDS product catalogue, one row per downloadable grid)
Output: cleaned lookup tables, completeness matrix, prioritised download request list,
        and a data-quality log.

Note: the file is metadata only. It contains no rainfall depths. Depths are inside the
downloadable grids referenced by the `url` column.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

INPUT = Path("/mnt/user-data/uploads/hirds.csv")
OUT = Path("results")
OUT.mkdir(exist_ok=True)

CASE_STUDY_REGIONS = {
    "Marlborough": "Case study 1: Marlborough (Kaikoura inventory area)",
    "Canterbury": "Case study 2: Banks Peninsula (Canterbury region)",
    "Waikato": "Case study 3: Coromandel (Thames-Coromandel lies within Waikato region; clip grid)",
}
COMPARATOR_REGIONS = {"New Zealand": "National V5.0 grid, for version comparison"}
EXPECTED_DURATIONS_MIN = [10, 20, 30, 60, 120, 360, 720, 1440, 2880, 4320, 5760, 7200]
EXPECTED_ARI = [1.58, 2, 5, 10, 20, 30, 40, 50, 60, 80, 100, 250]

log = []

def note(msg):
    log.append(msg)
    print(msg)

# ---------------------------------------------------------------------------
# 1. Load and clean
# ---------------------------------------------------------------------------
raw = pd.read_csv(INPUT)
note(f"Raw rows: {len(raw)}")

blank = raw["region"].isna()
note(f"Blank rows removed: {int(blank.sum())} (no region, duration, ARI or dates; no usable metadata)")
df = raw.loc[~blank].copy()

# ARI duplicate: float artefact, 1.58 stored as 1.58000004 in the raw file
raw_ari = df["ari"].copy()
df["ari"] = df["ari"].round(2)
n_artefact = int(((raw_ari - df["ari"]).abs() > 1e-12).sum())
note(f"ARI float artefacts normalised (e.g. 1.58000004 to 1.58): {n_artefact} rows")

df["duration_min"] = df["duration"].astype(int)
df["ari_years"] = df["ari"]
df["hirds_version"] = df["hirds-version"].astype(int)
df["grid_id"] = df["_id"]
df["region"] = df["region"].str.strip()

# Duration label, human readable
def label(minutes):
    if minutes < 60: return f"{minutes} min"
    if minutes < 1440: return f"{minutes // 60} h"
    return f"{minutes // 1440} d"
df["duration_label"] = df["duration_min"].map(label)

# Polygon bounding box (approximate boundary, see caveats)
coords = df["geojson.coordinates"].apply(lambda s: np.array(eval(s))[0])
df["bbox_min_lon"] = coords.apply(lambda c: c[:, 0].min())
df["bbox_max_lon"] = coords.apply(lambda c: c[:, 0].max())
df["bbox_min_lat"] = coords.apply(lambda c: c[:, 1].min())
df["bbox_max_lat"] = coords.apply(lambda c: c[:, 1].max())

# ---------------------------------------------------------------------------
# 2. Integrity checks
# ---------------------------------------------------------------------------
dup_key = ["region", "hirds_version", "duration_min", "ari_years"]
n_dup = int(df.duplicated(subset=dup_key).sum())
note(f"Duplicate region/version/duration/ARI keys after cleaning: {n_dup}")
if n_dup:
    raise SystemExit("Duplicate keys remain; investigate before proceeding.")

unexpected_dur = sorted(set(df["duration_min"]) - set(EXPECTED_DURATIONS_MIN))
unexpected_ari = sorted(set(df["ari_years"]) - set(EXPECTED_ARI))
note(f"Unexpected durations: {unexpected_dur or 'none'}")
note(f"Unexpected ARIs: {unexpected_ari or 'none'}")

# ---------------------------------------------------------------------------
# 3. Lookup tables
# ---------------------------------------------------------------------------
lookup = df[["grid_id", "region", "hirds_version", "duration_min", "duration_label",
             "ari_years", "dateMin", "dateMax", "url", "title",
             "bbox_min_lon", "bbox_max_lon", "bbox_min_lat", "bbox_max_lat"]]
lookup = lookup.sort_values(["region", "hirds_version", "duration_min", "ari_years"])
lookup.to_csv(OUT / "design_storm_lookup.csv", index=False)

# Completeness matrix: expected 12 durations x 12 ARIs per region and version
rows = []
for (region, ver), g in df.groupby(["region", "hirds_version"]):
    have = set(zip(g["duration_min"], g["ari_years"]))
    expected = {(d, a) for d in EXPECTED_DURATIONS_MIN for a in EXPECTED_ARI}
    missing = sorted(expected - have)
    rows.append({"region": region, "hirds_version": ver, "products_present": len(have),
                 "products_expected": len(expected), "missing": len(missing),
                 "complete": len(missing) == 0,
                 "case_study": region in CASE_STUDY_REGIONS})
completeness = pd.DataFrame(rows).sort_values(["case_study", "region"], ascending=[False, True])
completeness.to_csv(OUT / "completeness_matrix.csv", index=False)
note(f"Region/version combinations: {len(completeness)}; complete: {int(completeness['complete'].sum())}")

# Coverage matrix for the case study regions (duration x ARI, 1 = present)
cov_rows = []
for region in CASE_STUDY_REGIONS:
    g = df[(df["region"] == region) & (df["hirds_version"] == 4)]
    for d in EXPECTED_DURATIONS_MIN:
        r = {"region": region, "duration": label(d)}
        for a in EXPECTED_ARI:
            r[f"ARI_{a:g}"] = int(((g["duration_min"] == d) & (g["ari_years"] == a)).any())
        cov_rows.append(r)
pd.DataFrame(cov_rows).to_csv(OUT / "case_study_coverage_matrix.csv", index=False)

# ---------------------------------------------------------------------------
# 4. Download request list (prioritised)
# ---------------------------------------------------------------------------
TIERS = {
    # Tier 1: core design and event analysis
    1: {"durations": [60, 360, 1440], "aris": [2, 10, 100]},
    # Tier 2: sensitivity of conclusions to duration and return period
    2: {"durations": [10, 120, 2880], "aris": [5, 50, 250]},
}
def tier_of(d, a):
    for t, spec in TIERS.items():
        if d in spec["durations"] and a in spec["aris"]:
            return t
    return 3   # Tier 3: remainder, request only if needed

req_rows = []
for region in CASE_STUDY_REGIONS:
    g = df[(df["region"] == region) & (df["hirds_version"] == 4)]
    for _, r in g.iterrows():
        t = tier_of(r["duration_min"], r["ari_years"])
        if t <= 2:
            req_rows.append({
                "priority_tier": t, "region": region, "hirds_version": 4,
                "duration": r["duration_label"], "duration_min": r["duration_min"],
                "ari_years": r["ari_years"], "grid_id": r["grid_id"], "url": r["url"],
                "purpose": "design-storm comparison" if t == 1 else "sensitivity",
                "status": "to request",
            })
# National V5.0 grid for the version comparison (Tier 2 only, matching durations and ARIs)
nat = df[(df["region"] == "New Zealand") & (df["hirds_version"] == 5)]
for _, r in nat.iterrows():
    if tier_of(r["duration_min"], r["ari_years"]) <= 2:
        req_rows.append({
            "priority_tier": tier_of(r["duration_min"], r["ari_years"]), "region": "New Zealand",
            "hirds_version": 5, "duration": r["duration_label"], "duration_min": r["duration_min"],
            "ari_years": r["ari_years"], "grid_id": r["grid_id"], "url": r["url"],
            "purpose": "version comparison (V4 vs V5 needs V4 national grid too)", "status": "to request",
        })
requests = pd.DataFrame(req_rows).sort_values(["priority_tier", "region", "duration_min", "ari_years"])
requests.to_csv(OUT / "download_request_list.csv", index=False)

note(f"Download requests: {len(requests)} "
     f"(Tier 1: {int((requests['priority_tier']==1).sum())}, Tier 2: {int((requests['priority_tier']==2).sum())})")
note("Version comparison caveat: V4 covers 1986-2005 and V5.0 covers 2006-2025, so the two versions do not overlap in time. "
     "Any change between them mixes climate change with method change. The file has no V4 national grid, so a "
     "version-consistent comparison needs a V4 national grid or regional V4 grids, which must be confirmed with NIWA.")

# ---------------------------------------------------------------------------
# 5. Data-quality log and summary
# ---------------------------------------------------------------------------
Path(OUT / "data_quality_log.txt").write_text("\n".join(log) + "\n")
summary = {
    "raw_rows": int(len(raw)), "blank_rows_removed": int(blank.sum()),
    "clean_rows": int(len(df)), "ari_artefacts_normalised": n_artefact,
    "duplicate_keys": n_dup,
    "regions": int(df["region"].nunique()),
    "case_study_regions": list(CASE_STUDY_REGIONS),
    "all_case_study_regions_complete_v4": bool(
        completeness[(completeness["case_study"]) & (completeness["hirds_version"] == 4)]["complete"].all()),
    "download_requests": int(len(requests)),
    "caveat": "Bounding boxes are approximate; use official region boundaries for spatial joins.",
}
(OUT / "audit_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
