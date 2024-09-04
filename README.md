Here’s an expanded and detailed guide to help you set up your **AstroSpecVis** project from scratch on another system:

```markdown
# AstroSpecVis - Astrophysics Data Visualizer

## Project Overview

**AstroSpecVis** is a Flask-based web application designed to visualize astrophysics data (such as spectra from NIRSpec and MIRI instruments) using interactive 3D plots. The project combines Python for backend data processing and Plotly for visualization with a Tailwind CSS-powered frontend.

---

## Project Structure

```plaintext
- `app.py`: Main entry point for the Flask application.
- `astrospecvis/`: Main application package.
  - `models/`: Contains data processing, analysis, and plotting logic.
    - `data_loader.py`: Functions to load NIRSpec and MIRI spectra data.
    - `data_processor.py`: Functions to normalize and process spectra data.
    - `lightcurve_plotter.py`: Functions to generate interactive plots.
  - `static/`: Static assets like CSS, JS, and images.
    - `plots/`: Stores the generated plots as HTML files (e.g., variability maps, flux maps).
  - `templates/`: HTML templates for rendering Flask views.
    - `index.html`: Homepage template.
    - `upload.html`: File upload template.
    - `visualize.html`: Visualization page template.
  - `utils/`: Utility functions, such as data binning.
  - `uploads/`: Directory for storing uploaded FITS files (automatically created, ignored in `.gitignore`).
  - `output/`: Directory for any generated output files (automatically created, ignored in `.gitignore`).
- `config.json`: Configuration file storing paths and settings for data and files.
- `requirements.txt`: Python dependencies required to run the project.
- `.gitignore`: Git ignore file to exclude specific files and folders from version control.
- `package.json`: npm package management file for frontend assets (CSS, JS).
- `tailwind.config.js`: Tailwind CSS configuration file for customizing the styling of the frontend.
```

---

## Setup Instructions

### Prerequisites

Ensure you have the following software installed on the system:

1. **Python 3.8 or higher**: Required for the Flask backend.
2. **Node.js** (and npm): Required for managing frontend dependencies and building Tailwind CSS.
3. **Virtual Environment** (recommended): Isolate Python packages.
4. **Git**: For version control.

### Step 1: Clone the Repository

First, you'll need to clone your GitHub repository to the new machine.

```bash
git clone git@github.com:FardinIqbal/AstroSpecVis.git
cd AstroSpecVis
```

### Step 2: Python Environment Setup

#### Option 1: Using Virtual Environment (Recommended)

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

2. Activate the virtual environment:

   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

#### Option 2: Without Virtual Environment (Not Recommended)

Skip the virtual environment setup and install the dependencies globally, but note this can interfere with other Python projects.

### Step 3: Install Python Dependencies

With the virtual environment activated, install the required Python packages.

```bash
pip install -r requirements.txt
```

This will install:

- Flask: For building the web app.
- Plotly: For creating interactive 3D visualizations.
- astropy, numpy, and scipy: For processing astronomical data.

### Step 4: Frontend Setup (Tailwind CSS)

If you plan to modify or build the frontend (styles), follow these steps:

1. Install npm packages:

   ```bash
   npm install
   ```

2. Build the Tailwind CSS files:

   ```bash
   npm run build-css
   ```

This will compile the Tailwind CSS into a single `styles.css` file located in `static/css/`.

### Step 5: Configuring the Application

1. **config.json**: This file contains important paths and settings for the application. Make sure to update the paths in `config.json` to the correct locations of your NIRSpec, MIRI spectra, or other data files.

```json
{
  "data_paths": {
    "flux_nirspec_b": "path/to/NIRSpec/flux_data.fits",
    "mjdarr": "path/to/NIRSpec/mjdarr.fits",
    "nirspec_wlarr": "path/to/NIRSpec/wavelength_data.fits",
    "miri_spectra": "path/to/MIRI/spectra.fits"
  }
}
```

**Note**: Ensure that large data files are not pushed to the repository (already ignored by `.gitignore`).

### Step 6: Running the Application

Once everything is set up, run the Flask application. If using the default setup, this will start a local server on `http://127.0.0.1:5000`.

```bash
python app.py
```

### Step 7: Access the Application

Open your browser and visit `http://127.0.0.1:5000` to access the homepage.

- You can upload a `.fits` file using the upload form.
- After upload, the file will be processed, and visualizations (variability map, flux map, etc.) will be displayed.

---

## Deployment Instructions

To deploy this application on a production server (e.g., DigitalOcean, AWS, Heroku), use a production-ready WSGI server like **Gunicorn** or **uWSGI**. Here are basic steps:

1. Install **Gunicorn** (if not already installed):
   ```bash
   pip install gunicorn
   ```

2. Run Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

This will start the app with 4 workers and make it accessible via `0.0.0.0` (public IP address).

### Using Nginx and Gunicorn (Recommended)

For more robust production deployment, set up **Nginx** as a reverse proxy and use **Gunicorn** to serve the app.

---

## Notes

- **Uploaded Files**: Uploaded `.fits` files are stored in the `uploads/` directory.
- **Generated Files**: Output files such as plots are stored in `static/plots/`. These files are generated after processing the uploaded data.
- **Modifying Styles**: Use Tailwind CSS for modifying the frontend styles. Make sure to rebuild the CSS using `npm run build-css` after making changes.
- **Data Files**: Large data files are ignored from version control using `.gitignore`. Make sure to add them to the correct path before running the app.

---

## Troubleshooting

1. **File Upload Issues**: Ensure that the `uploads/` directory is writable.
2. **Large Data Files**: If you need to handle large data files, consider using Git Large File Storage (LFS).
3. **Dependency Conflicts**: Use a virtual environment to prevent conflicts between Python packages.
4. **Production Setup**: Use a production server like **Gunicorn** with **Nginx** for deployment.

---

With this guide, you should be able to set up the AstroSpecVis project on any server or local environment.
```
