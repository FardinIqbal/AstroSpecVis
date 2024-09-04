# src/utils/utils.py

import numpy as np


def median_bin(input_array: np.ndarray, bin_size: int) -> np.ndarray:
    """
    Perform median binning on a 1D array, ignoring NaN values.

    Args:
        input_array (np.ndarray): Input 1D array to be binned.
        bin_size (int): Number of elements to bin together.

    Returns:
        np.ndarray: Binned array.
    """
    end_index = bin_size * (len(input_array) // bin_size)
    return np.nanmedian(input_array[:end_index].reshape(-1, bin_size), axis=1)


import numpy as np


def bin_flux_array(flux_data, bin_size):
    """
    Bin the flux data along the time axis to reduce the number of timepoints.

    Args:
        flux_data (np.ndarray): The original 2D flux data array.
        bin_size (int): The size of the bin.

    Returns:
        np.ndarray: The binned flux data array.
    """
    # Ensure bin_size is an integer
    bin_size = int(bin_size)

    # Get the shape of the input data
    num_wavelengths, num_timepoints = flux_data.shape

    # Check if num_timepoints and bin_size are compatible
    if not isinstance(num_timepoints, int) or not isinstance(bin_size, int):
        raise ValueError("num_timepoints and bin_size must be integers")

    binned_timepoints = num_timepoints // bin_size  # Integer division
    binned_flux = np.nanmean(flux_data[:, :binned_timepoints * bin_size].reshape(
        num_wavelengths, binned_timepoints, bin_size), axis=2)

    return binned_flux
