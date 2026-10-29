# Were Roads Designed for the Storms That Triggered Their Landslides?
## Design rainfall, road drainage and slope failure in Marlborough, Banks Peninsula and Coromandel, New Zealand

**Candidate:** Christian Somtoo Obiechina
**Proposed supervisor:** Dr Ellen Robson (primary). Possible co-supervisors, to be confirmed: Liam Wotherspoon (University of Auckland) and Thomas Robinson (Senior Lecturer, University of Canterbury)
**Proposed start:** [Date]
**Duration:** 3 years full-time
**Status:** Draft research proposal. Phase 1 data audit complete.

---

## 1. Background and problem

Landslides are the most costly natural hazard in Aotearoa New Zealand, and when they affect the road network they disrupt communities, freight and emergency services. Road drainage, cut slopes and fill embankments are designed for a stated rainfall intensity, usually expressed as a design storm for a given duration and average recurrence interval (ARI). The High Intensity Rainfall Design System (HIRDS) provides these design depths across New Zealand.

If the storms that trigger road slips exceed the design storm for the location, the failure may reflect design assumptions that no longer hold, poor drainage maintenance, or slope conditions that design rainfall does not capture. Existing work has mapped landslides and modelled rainfall thresholds, but few studies test directly whether road-related failures occur where the design rainfall has been exceeded. Road construction and management practice, which the design process assumes, is rarely recorded in publicly available data.

## 2. Research questions

- **RQ1.** For road-related landslides in the three case study areas, what return periods do the triggering storms correspond to, when compared with the HIRDS design depths for the same location and duration?
- **RQ2.** Does exceedance of the design storm improve prediction of road slip occurrence beyond slope, geology and road-type variables?
- **RQ3.** How have HIRDS design depths changed between versions V4 (1986 to 2005) and V5.0 (2006 to 2025), and how would that change alter design exceedance probabilities for road drainage?

## 3. Hypotheses

- **H1.** Road slips occur more often where the event rainfall exceeds the 10-year ARI design depth for the matching duration than at matched control locations.
- **H2.** Adding design exceedance to a model with slope, geology and road-class variables improves out-of-sample prediction of slip occurrence, measured on spatially held-out blocks.
- **H3.** Design depths differ between V4 and V5.0 at the case study locations by more than the method uncertainty. The null hypothesis is that differences are within that uncertainty.

H3 is tested as a change in design standard. It is not attributed to climate change, because the two versions do not overlap in time and differ in method.

## 4. Study area

- **Marlborough**: 2016 Kaikōura earthquake landslide inventory, with road exposure on State Highway 1 and regional roads.
- **Banks Peninsula (Canterbury)**: steep volcanic slopes with a dense local road network.
- **Coromandel (Waikato region)**: Cyclone Gabrielle inventory (2023) with State Highway 25 and 25A slips. The HIRDS grid covers the whole Waikato region, so grid values must be clipped to the Coromandel boundary.

## 5. Data

| Dataset | Source | Use | Status |
|---|---|---|---|
| HIRDS V4 and V5.0 design grids | NIWA | Design depths, durations 10 min to 5 days, ARI 1.58 to 250 years | Catalogue audited (2,448 products, 17 regions). Grid downloads required; check licence and cost |
| NZ Landslide Database | Earth Sciences New Zealand | Landslide locations, dates, size, type | Upgraded October 2025 (over 500,000 landslides in stages). Confirm downloadable release |
| Kaikōura 2016 inventory | GeoNet / GNS Science | Marlborough slides | Public, confirm format |
| Cyclone Gabrielle inventory | USGS and partners | Coromandel slides, attributes including movement type and mapping certainty | Public domain |
| Event rainfall | NIWA VCSN (daily, about 5 km grid) and station records | Storm depth at each slide location | Access and licence to confirm |
| Elevation | LINZ LiDAR DEM | Slope, curvature, aspect | Public |
| Geology | GNS Science QMAP | Lithology and soil units | Public |
| Road network | LINZ road centrelines | Road class and proximity | Public |
| Road closures | NZTA TREIS and road events | Closure duration as severity proxy | Historical coverage to confirm |
| Road construction and maintenance records | Marlborough, Canterbury and Thames-Coromandel councils | Design standard, drainage works, repair history | Not public. Request under LGOIMA. Response within 20 working days, extendable |

**Phase 1 result.** The HIRDS catalogue audit (`coverage_audit.py`) cleaned 2,449 raw rows to 2,448 products. One blank row was removed. Twelve ARI values stored as 1.58000004 were normalised to 1.58. No duplicate keys remain. All three case study regions have complete grids for V4 (144 of 144 duration and ARI combinations). Seventy-two prioritised downloads are listed in `download_request_list.csv`. Tier 1 contains 36 products for design-storm comparison. Tier 2 contains 36 products for sensitivity analysis.

**Structural constraint.** V4 covers 1986 to 2005 and V5.0 covers 2006 to 2025, so the two versions do not overlap in time. The catalogue contains V5.0 for the national grid only. A version-consistent comparison for H3 therefore needs a V4 national grid, or regional V4 and V5.0 grids for the same period, confirmed with NIWA before RQ3 is attempted.

## 6. Methods

**Phase 2: Spatial data engineering (months 1 to 6).** Replace the approximate HIRDS bounding boxes with official region boundaries. Read the grid files, clip the Waikato grid to Coromandel, and build a reproducible pipeline from landslide points to design depth at each location.

**Phase 3: Event return periods (months 6 to 12).** For each road-related landslide with a known date, extract daily rainfall for the storm duration. Compute the event return period by interpolating the HIRDS design depths for the matching duration, using a log-scale interpolation between ARI values. Validate the interpolation by reproducing HIRDS values at grid points. Report the interpolation method and its uncertainty.

**Phase 4: Occurrence model (months 12 to 24).** Use a matched case-control design. Control points are sampled along the same road network, matched on slope class, geology and road class, and selected where no slip is recorded. Fit a conditional logistic regression with and without design exceedance. Compare the models with block cross-validation over spatial blocks, reporting AUC, Brier score and calibration. Block cross-validation limits optimistic results from spatial autocorrelation.

**Phase 5: Design standard change (months 18 to 30).** Compare V4 and V5.0 design depths at the case study locations, quantify differences against method uncertainty, and assess how exceedance probabilities change. Present this as a change in design standard, not as evidence of climate attribution.

**Phase 6: Synthesis and severity (months 24 to 36).** Where closure records and construction records are available, test whether design exceedance and construction variables are associated with longer closures. Synthesise results across the three regions.

## 7. Validation and robustness

- Interpolation checks against HIRDS grid values at known points.
- Sensitivity of H1 and H2 to the choice of duration (1 h, 6 h, 24 h) and ARI (2, 10, 100 years).
- Spatial holdout: train on two regions and test on the third.
- Sensitivity to control-point sampling and matching rules.
- Reporting of absence bias: the NZLD records mapped landslides, not all landslides, so controls are not confirmed as stable.

## 8. Expected contributions

1. A reproducible method linking HIRDS design rainfall to landslide events and road slip occurrence, with code and an audit trail.
2. Evidence on whether road-related slips occurred where design storms were exceeded, across three contrasting New Zealand settings.
3. A quantified comparison of design depths between HIRDS V4 and V5.0, and its implications for road drainage design.
4. A data release that identifies the missing road construction and maintenance records, with a case for their collection.

To my knowledge, no published study tests road slip occurrence directly against HIRDS design exceedance in New Zealand. This must be confirmed in the literature review in Year 1.

## 9. Risks and mitigation

| Risk | Mitigation |
|---|---|
| HIRDS grids are costly or restricted | Confirm licence and cost in Month 1. Limit downloads to Tier 1 first |
| Road construction records are refused or delayed | Submit LGOIMA requests in Month 1. Design Phase 4 to run without them |
| Landslide inventory is incomplete | Treat absence as unknown, use matched controls, and report the bias |
| VCSN resolution misses local storm peaks | Report the limitation. Test sensitivity with station records where available |
| V4 and V5.0 cannot be compared consistently | Restrict H3 to what the data support, and state this clearly |
| Results are correlational | Frame conclusions as associations, not causal effects of design |

## 10. Ethics and data governance

No human participants are involved. Landslide and road data are either public or obtained under LGOIMA. The HIRDS and VCSN licence terms will be followed, and any redistributed data will be checked against them. Code and derived non-restricted outputs will be released.

## 11. Timeline

| Period | Milestone |
|---|---|
| Year 1, months 1 to 6 | Literature review, data requests, HIRDS downloads, spatial pipeline |
| Year 1, months 7 to 12 | Event return periods, validation of interpolation |
| Year 2, months 13 to 24 | Occurrence model, spatial cross-validation, first paper |
| Year 2, months 19 to 30 | Design standard comparison (H3), second paper |
| Year 3, months 25 to 36 | Closure and severity analysis, synthesis, thesis submission |

## 12. Fit with supervisor and programme

This project extends the road landslide research in the Department of Civil and Environmental Engineering at the University of Canterbury. It draws on the expertise in landslide hazards, road infrastructure and geotechnical engineering represented in the supervisory team. The candidate's data science background supports the spatial analysis, statistical modelling and reproducible workflow the project requires. The candidate does not yet have formal geotechnical or landslide field experience, and the training plan addresses this directly.

---

*Attachments: `coverage_audit.py`, `design_storm_lookup.csv`, `completeness_matrix.csv`, `case_study_coverage_matrix.csv`, `download_request_list.csv`, `data_quality_log.txt`, `audit_summary.json`.*
