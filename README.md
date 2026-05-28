# GLIMPSE

**Getting Light IMprints from Planetary Spectral Emissions**

Interactive JWST exoplanet transit spectroscopy visualizer. Browse the JWST observation catalog, render transmission spectra with 1-sigma error bars, overlay molecular absorption bands, and export publication-ready data.

[Live Demo](https://glimpse-jwst.vercel.app) - [API](https://astrospecvis.onrender.com)

---

## Hero

- Curated catalog of JWST-observed exoplanets (WASP-39 b and beyond, NIRSpec + NIRISS, 0.6-5.3 um)
- Transmission spectra rendered to HTML5 Canvas with 1-sigma / 2-sigma uncertainty bands
- Molecular band overlays: H2O, CO2, CO, CH4, SO2, NH3, Na/K
- Spectral time-series heatmap and transit light curve views
- CSV / JSON / PNG export
- WCAG 2.1 AA compliant with screen-reader data tables and keyboard navigation

---

## What it is

GLIMPSE is a full-stack visualization tool for exoplanet atmospheres. When a planet transits its host star, a fraction of starlight filters through its atmosphere; molecules absorb at characteristic wavelengths, producing a spectral fingerprint. GLIMPSE renders those fingerprints interactively from real JWST archive data and physically-motivated demo models.

The transmission spectrum plots transit depth `d = (Rp/R*)^2` in ppm against wavelength. Feature amplitudes are 10-1000 ppm for gas giants and 1-100 ppm for terrestrial planets. GLIMPSE marks where each molecule absorbs so users can reason about atmospheric composition.

---

## Key features

### Visualization
- Transmission spectrum with 1-sigma and 2-sigma uncertainty bands
- 2D spectrogram heatmap across wavelength and orbital phase
- Transit light curves at user-selected wavelengths
- Canvas rendering (no chart library) for 60fps on mobile

### Molecular band overlays

| Molecule | Bands (um) | Significance |
|----------|------------|--------------|
| H2O | 1.4, 1.9, 2.7 | Habitability indicator |
| CO2 | 4.3, 15.0 | Carbon cycle, greenhouse |
| CO | 2.3, 4.6 | Atmospheric chemistry |
| CH4 | 2.3, 3.3, 7.7 | Biosignature candidate |
| SO2 | 4.0, 7.3, 8.7 | Volcanic / photochemistry |
| NH3 | 1.5, 2.0, 10.5 | Nitrogen chemistry |
| Na/K | 0.59, 0.77 | Alkali metals, hot atmospheres |

### Data sources
- **Demo mode** — physically-motivated simulated spectra grounded in published JWST observations
- **MAST mode** — live queries to the Mikulski Archive for Space Telescopes via `astroquery`
- **Exoplanet parameters** — NASA Exoplanet Archive

### Controls
- Spectral binning (5-100 points)
- Per-molecule band toggles
- CSV / JSON / PNG export
- Colorblind-safe Okabe-Ito palette

### Accessibility
- WCAG 2.1 AA compliant
- `aria-label` chart descriptions + hidden data tables
- Keyboard navigation of data points, focus indicators, skip links
- 4.5:1 text contrast, 3:1 UI contrast, 200% zoom without loss of function

---

## Architecture

```
+-------------------------------------------------------------+
|                      Next.js 16 / React 19                   |
|                        (Vercel)                              |
|  Target Selector  |  Spectrum Canvas  |  Spectrogram / LC    |
+------------------------------+------------------------------+
                               | HTTPS (JSON)
                               v
+-------------------------------------------------------------+
|                     FastAPI (Python 3.11)                    |
|                       (Render, $0 tier)                      |
|  /api/mast/targets  |  /api/mast/demo-data  |  /api/mast/... |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|   MAST Archive (STScI)  +  NASA Exoplanet Archive           |
|   JWST NIRSpec / NIRISS transit FITS via astropy            |
+-------------------------------------------------------------+
```

The frontend also ships Next.js API routes (`apps/web/src/app/api/*`) as a resilience layer so the app stays interactive when the free-tier Render backend cold-starts.

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Frontend framework | Next.js 16 (App Router), React 19 |
| Language (web) | TypeScript 5 |
| Styling | Tailwind CSS 4 |
| Animation | Framer Motion 12 |
| Charts | HTML5 Canvas (custom renderer) |
| 3D | three.js + @react-three/fiber + drei |
| Icons | lucide-react |
| Backend framework | FastAPI |
| Language (api) | Python 3.11 |
| Astronomy | astropy >=6.0, astroquery >=0.4.7 |
| Numerics | numpy, scipy |
| ASGI server | uvicorn + uvloop + httptools |
| Frontend host | Vercel |
| Backend host | Render (free tier) |

---

## Quick start

### Prerequisites
- Node.js 20+
- Python 3.11+
- npm or pnpm or bun

### Install and run

```bash
git clone https://github.com/FardinIqbal/GLIMPSE.git
cd GLIMPSE

# Frontend
cd apps/web
npm install      # or: pnpm install / bun install

# Backend
cd ../api
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run both together from the repo root:

```bash
npm install
npm run dev      # concurrently boots web on :3000 and api on :8000
```

Or run separately:

```bash
# Terminal 1
cd apps/api && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2
cd apps/web && npm run dev
```

Open http://localhost:3000.

### Environment

Frontend:
- `NEXT_PUBLIC_API_URL` — backend URL (optional; app falls back to Next.js API routes)

Backend:
- `FRONTEND_URL` — CORS origin
- `PYTHON_VERSION` — `3.11`

---

## API reference

Base URL: `https://astrospecvis.onrender.com` (prod) or `http://localhost:8000` (local).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Health + metadata |
| GET | `/health` | Render health check |
| GET | `/api/mast/targets` | List curated JWST exoplanet targets |
| GET | `/api/mast/demo-data/{target}?bin_size=20` | Simulated transit spectrum |
| GET | `/api/mast/real-data/{target}` | Live JWST data from MAST |
| GET | `/api/mast/exoplanet/{target}` | NASA Exoplanet Archive parameters |
| GET | `/api/mast/molecular-bands` | Molecular absorption band catalog |

Example target response:

```json
{
  "name": "WASP-39 b",
  "type": "Hot Saturn",
  "features": ["Water", "Carbon Dioxide", "Sulfur Dioxide"],
  "proposal": "ERS-1366",
  "description": "Benchmark hot Saturn with detailed atmospheric characterization"
}
```

---

## Deployment

### Frontend — Vercel
- Root: repo root; build via `apps/web`
- `vercel.json` at repo root handles monorepo build + `ignoreCommand` to skip redundant builds
- Set `NEXT_PUBLIC_API_URL` if pointing at a non-default backend

### Backend — Render ($0 tier)
Blueprint deploy via the checked-in `render.yaml`:

```yaml
services:
  - type: web
    name: glimpse-api
    runtime: python
    plan: free
    rootDir: apps/api
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
```

Free-tier cold starts are masked by the Next.js API routes that shadow the Python backend.

---

## Data attribution

- Transit spectroscopy — [MAST Archive](https://mast.stsci.edu) (STScI)
- Planetary parameters — [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu)
- JWST operated by STScI for NASA / ESA / CSA
- JWST Early Release Science Program 1366 (WASP-39 b)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgments

The astronomical Python community: astropy, astroquery, Space Telescope Science Institute. Mobile/accessibility design informed by the NASA Web Design System, U.S. Web Design System, and STScI's Jdaviz.
