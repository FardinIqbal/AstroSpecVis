# Architectural Decision Records

Each entry documents a non-obvious engineering choice, its alternatives, and why I picked what I picked.

---

## ADR 1: Two-tier deployment (Vercel frontend, Render backend)

**Status:** accepted

**Context:**
GLIMPSE has a TypeScript frontend and a Python backend. Three options:

1. **Single platform**: frontend and backend on the same provider (e.g., Vercel with Python serverless functions, or Render with Next.js).
2. **Two-tier** (this design): Next.js on Vercel, FastAPI on Render.
3. **Self-hosted**: a single VPS running both via Docker.

**Decision:**
Two-tier.

**Consequences:**

- Pro: each platform's strengths match the workload. Vercel does Next.js better than anyone (edge functions, image optimization, zero-config builds). Render handles long-running Python processes well.
- Pro: the backend's heavy dependencies (astropy ~120 MB, astroquery, numpy, scipy) live on Render where cold-start does not matter, not on Vercel where serverless cold starts hurt.
- Pro: zero-cost hosting for low traffic (Vercel free tier + Render free tier).
- Con: two CORS configurations. Two deployment pipelines.
- Con: cold start on the Render free tier (the backend spins down after inactivity, takes 30-60 seconds to wake).

For a portfolio project with sporadic traffic, the cold-start trade is acceptable. For production, the backend would be on a paid Render plan or moved to Cloud Run / similar.

---

## ADR 2: Heuristic column detection in FITS parser

**Status:** accepted

**Context:**
Different JWST instrument modes (NIRSpec x1d, NIRISS x1d, MIRI x1d) use different column naming conventions in their FITS files. Two options:

1. **Per-instrument special cases**: detect `INSTRUME` keyword, dispatch to a parser written specifically for that instrument's conventions.
2. **Heuristic column lists** (this design): try a list of common column names and use the first match.

**Decision:**
Heuristic.

**Consequences:**

- Pro: handles new or unusual files without code changes. As long as the file uses `FLUX`, `SCI`, or `DATA` for the flux column, it works.
- Pro: simpler. One code path instead of N.
- Pro: maintainable. Adding support for a new instrument is a one-line addition to the column-candidates list.
- Con: silent failures. If a file uses an unrecognized column name, the parser returns no flux data without indicating why.
- Con: ambiguous. If a file has both `FLUX` and `SCI`, the parser picks the first match, which may not be the right one.

For a tool that primarily handles JWST x1d products, the heuristic catches >95% of cases. Rare exceptions can be handled with explicit special cases.

---

## ADR 3: Median normalization over mean

**Status:** accepted

**Context:**
Spectra are normalized to a baseline of 1.0 before plotting. Two options:

1. **Mean normalization**: `flux / mean(flux)`.
2. **Median normalization** (this design): `flux / median(flux)`.

**Decision:**
Median.

**Consequences:**

- Pro: robust to absorption features. A spectrum with a deep absorption band has its mean pulled down by the band; the median is unaffected.
- Pro: better baseline. The "typical" flux level is the median, by definition.
- Pro: less sensitive to outliers. Cosmic-ray hits or detector artifacts do not skew the normalization.
- Con: median is slower to compute on large arrays (sort O(n log n) vs mean O(n)). Negligible at our scales.

Mean normalization is the textbook choice for symmetric distributions. Spectra with absorption features are not symmetric. Median wins.

---

## ADR 4: Okabe-Ito palette for molecular bands

**Status:** accepted

**Context:**
The molecular band overlays use distinct colors so the user can tell H2O from CO2 from CH4 at a glance. Two options:

1. **Standard rainbow palette** (e.g., matplotlib's `viridis` or `tab10`).
2. **Colorblind-safe palette** (this design): the [Okabe-Ito scheme](https://jfly.uni-koeln.de/color/), specifically designed to be distinguishable across deuteranopia, protanopia, and tritanopia.

**Decision:**
Okabe-Ito.

**Consequences:**

- Pro: distinguishable for ~8% of male users (deuteranopia or protanopia) and ~0.5% of female users.
- Pro: still pleasant to colorblind-typical users (the palette is well-balanced).
- Con: only 8 colors in the standard scheme. If we ever need more than 8 distinct molecules, we need to extend the palette carefully.

For scientific tools, accessibility is not optional. A colorblind reviewer who cannot distinguish red from green should still be able to use GLIMPSE.

---

## ADR 5: Streaming FITS files instead of caching

**Status:** accepted

**Context:**
JWST FITS files are 1-100 MB each. Two options:

1. **Cache on backend disk**: download once, serve from local cache.
2. **Stream from MAST** (this design): download fresh on every request, process in memory, discard.

**Decision:**
Stream.

**Consequences:**

- Pro: no disk management. No cache eviction policy, no disk full risk.
- Pro: always fresh. If MAST updates a file, we get the update on next request.
- Pro: matches Render free tier. Free tier has limited persistent disk.
- Con: every request hits MAST. Slower per-request, more bandwidth used.
- Con: depends on MAST availability.

For a project with sporadic traffic, streaming is fine. For production scale, an in-memory or Redis cache would be the right addition.

---

## ADR 6: Internal API routes proxying to backend

**Status:** accepted

**Context:**
The frontend needs to call the backend. Two options:

1. **Direct calls**: frontend fetches from `https://astrospecvis.onrender.com/api/...`.
2. **Proxy via Next.js API routes** (this design): frontend fetches from `/api/mast/...`, which the Next.js server forwards to Render.

**Decision:**
Proxy.

**Consequences:**

- Pro: same-origin requests. No CORS headers needed (Next.js handles the cross-origin call server-side).
- Pro: the backend URL is hidden. The frontend's network tab shows only `/api/...` paths.
- Pro: easier auth (if needed, the proxy can attach auth headers without exposing keys to the client).
- Con: extra hop. Each request goes browser → Vercel → Render, adding latency.
- Con: Vercel function invocation cost (negligible at low traffic).

For a project where the backend URL might change or where we want to add auth later, proxying is the more flexible choice. The latency cost is minimal compared to the FITS parsing time.

---

## ADR 7: Featured-target catalog hardcoded in source

**Status:** accepted

**Context:**
The TargetSelector dropdown shows curated exoplanets. Two options:

1. **Database-driven**: store the list in Postgres, edit via admin UI.
2. **Hardcoded** (this design): a Python list in `mast_client.py`.

**Decision:**
Hardcoded.

**Consequences:**

- Pro: no database to operate. The catalog updates via PR, deploy, done.
- Pro: version-controlled. Catalog changes are visible in git.
- Pro: simpler deployment. No DB connection string for catalog data.
- Con: editing requires a deploy.
- Con: cannot easily expose a "submit a new target" feature to users.

For curated content that changes maybe weekly, hardcoded is the right call. If the project grew to crowd-source target submissions, a database would be the upgrade.
