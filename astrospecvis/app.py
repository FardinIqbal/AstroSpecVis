import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from astrospecvis.models.data_loader import load_nirspec_data, load_miri_spectra, extract_miri_data
from astrospecvis.models.data_processor import normalize_spectrum
from astrospecvis.models.lightcurve_plotter import plot_enhanced_lightcurve_map, plot_specific_wavelength_lightcurves

# Initialize Flask app
app = Flask(__name__)

# Configure logging for better error tracking and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the configuration from a JSON file
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Set upload folder and allowed file types
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'fits'}  # Only allow FITS files for upload
app.secret_key = 'your_secret_key'  # Used for session management (change this in production)

# Create upload directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check if the file has the correct extension
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route for the home page
@app.route('/')
def index():
    """Render the home page with upload option."""
    return render_template('index.html')

# Route for uploading FITS files
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload and redirection to the visualization page."""
    if request.method == 'POST':
        # Check if a file is part of the request
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # Check if a file was selected
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # If the file is valid, save it to the upload folder
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Ensure the filename is safe
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logger.info(f"Saving uploaded file to {file_path}")
            file.save(file_path)
            return redirect(url_for('visualize', filename=filename))  # Redirect to visualization after upload

    return render_template('upload.html')

# Route for visualizing the uploaded FITS file
@app.route('/visualize/<filename>')
def visualize(filename):
    """Process the uploaded FITS file and generate plots for visualization."""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Visualizing file: {filename}")

        # Determine whether the file is NIRSpec or MIRI based on the filename
        if 'nirspec' in filename.lower():
            logger.info(f"Processing NIRSpec data for {filename}")
            # Load NIRSpec data from the FITS file
            flux_data, times, wavelengths = load_nirspec_data(
                config['data_paths']['flux_nirspec_b'],
                config['data_paths']['mjdarr'],
                config['data_paths']['nirspec_wlarr']
            )
        elif 'miri' in filename.lower():
            logger.info(f"Processing MIRI data for {filename}")
            # Load and extract MIRI data
            miri_table = load_miri_spectra(config['data_paths']['miri_spectra'])
            times, wavelengths, _, spectra, _ = extract_miri_data(miri_table)
            flux_data = normalize_spectrum(spectra)  # Normalize the spectrum for visualization
        else:
            flash('Unsupported file type')
            return redirect(url_for('upload_file'))

        # Generate various plots for visualization
        variability_plot = plot_enhanced_lightcurve_map(
            flux_data, wavelengths, times,
            f"{filename} Variability Map",
            bin_size=25,  # Add the bin size here
            output_file=os.path.join(app.static_folder, 'plots', f'{filename}_variability.html'),
            plot_type='variability'
        )

        flux_plot = plot_enhanced_lightcurve_map(
            flux_data, wavelengths, times,
            f"{filename} Flux Map",
            bin_size=25,  # Specify bin size explicitly
            output_file=os.path.join(app.static_folder, 'plots', f'{filename}_flux.html'),
            plot_type='flux'  # Generate a flux map
        )

        specific_lightcurves = plot_specific_wavelength_lightcurves(
            flux_data, wavelengths, times,
            f"{filename} Specific Wavelength Light Curves",
            output_file=os.path.join(app.static_folder, 'plots', f'{filename}_lightcurves.html')
        )

        logger.info(f"Plots generated successfully for {filename}")

        # Render the visualization page with generated plot files
        return render_template('visualize.html',
                               filename=filename,
                               variability_plot=f'{filename}_variability.html',
                               flux_plot=f'{filename}_flux.html',
                               specific_lightcurves=f'{filename}_lightcurves.html')

    except Exception as e:
        # Log any errors encountered during processing
        logger.error(f"An error occurred during visualization: {str(e)}", exc_info=True)
        return "An error occurred while processing the file. Check the logs for details.", 500

# Run the app in debug mode for easier development debugging
if __name__ == '__main__':
    app.run(debug=True)
