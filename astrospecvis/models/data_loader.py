# src/data_processing/data_loader.py

from astropy.table import Table
import astropy.io.fits as fits
import numpy as np


def load_miri_spectra(file_path: str) -> Table:
    """
    Load MIRI spectra from a FITS file.

    Args:
        file_path (str): Path to the MIRI spectra FITS file.

    Returns:
        Table: Astropy Table containing the MIRI spectra data.
    """
    return Table.read(file_path)


def print_miri_columns(miri_table: Table):
    """
    Print the column names of the MIRI data table.

    Args:
        miri_table (Table): Astropy Table containing MIRI spectra data.
    """
    print("MIRI data columns:")
    for col in miri_table.colnames:
        print(f"- {col}")


def extract_miri_data(miri_table: Table) -> tuple:
    """
    Extract and restructure relevant data from MIRI spectra table.

    Args:
        miri_table (Table): Astropy Table containing MIRI spectra data.

    Returns:
        tuple: Contains modified_julian_dates, wavelengths_a, wavelengths_b, spectra_a, spectra_b
    """
    print_miri_columns(miri_table)

    # Extract data
    wavelengths_a = miri_table['wla']
    wavelengths_b = miri_table['wlb']
    spectra_a = miri_table['fluxa']
    spectra_b = miri_table['fluxb']
    modified_julian_dates = miri_table['MJD']

    # Get unique wavelengths and times
    unique_wavelengths_a = np.unique(wavelengths_a)
    unique_wavelengths_b = np.unique(wavelengths_b)
    unique_times = np.unique(modified_julian_dates)

    # Reshape spectra into 2D arrays
    spectra_a_2d = spectra_a.reshape(len(unique_wavelengths_a), -1)
    spectra_b_2d = spectra_b.reshape(len(unique_wavelengths_b), -1)

    print(f"Reshaped MIRI data: spectra_a_2d shape: {spectra_a_2d.shape}, spectra_b_2d shape: {spectra_b_2d.shape}")
    print(f"Unique wavelengths A: {len(unique_wavelengths_a)}, B: {len(unique_wavelengths_b)}")
    print(f"Unique times: {len(unique_times)}")

    return unique_times, unique_wavelengths_a, unique_wavelengths_b, spectra_a_2d, spectra_b_2d


def load_nirspec_data(flux_file: str, mjd_file: str, wavelength_file: str) -> tuple:
    """
    Load NIRSpec data from FITS files.

    Args:
        flux_file (str): Path to the flux data FITS file.
        mjd_file (str): Path to the Modified Julian Date data FITS file.
        wavelength_file (str): Path to the wavelength data FITS file.

    Returns:
        tuple: Contains flux_data, modified_julian_dates, and wavelengths numpy arrays.
    """
    flux_data = fits.getdata(flux_file)
    modified_julian_dates = fits.getdata(mjd_file)
    wavelengths = fits.getdata(wavelength_file)
    return flux_data, modified_julian_dates, wavelengths
